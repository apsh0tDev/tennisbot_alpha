import asyncio
import json
import constants
from db import db
from rich import print
from loguru import logger
from utils import verifier
from draftkings_markets import marker_sorter
from connection import scrape, scrape_with_proxy


#General call - Every 20 minutes - Gathers all matches in one place
async def scrape_data():
        data = {
            'cmd' : 'request.get',
            'url' : constants.draftkings_url,
            'requestType' : 'request'
        }
        response = await scrape(data, "Draftkings")
        try:
              load = json.loads(response)
              if 'featuredDisplayGroup' in load and "featuredSubcategories" in load['featuredDisplayGroup']:
                    subcats = load['featuredDisplayGroup']['featuredSubcategories']
                    event_groups = [{"eventGroupId" : item['eventGroupId'], "eventGroupName" : item['eventGroupName']} for item in subcats[0]['featuredEventGroupSubcategories']]

                    #These event groups are actually the tournaments.
                    #Let's check first in the database what tournaments BetMGM has and according to that, we filter the groups
                    #We want to avoid as many unnecesary calls as possible
                    table_response = db.table("matches_list").select("tournament").match({'source' : 'BetMGM'}).execute()
                    #remove the duplicates
                    tournaments = [item['tournament'] for item in table_response.data]
                    tournaments = list(set(tournaments))
                    tasks = []
                    for tournament in event_groups:
                          tournament_name = tournament['eventGroupName'].split(" - ")[0].strip()
                          if tournament_name in tournaments:
                                tasks.append(scrape_tournaments(tournament['eventGroupId']))

                    #print(event_groups)
                    await asyncio.gather(*tasks)
              
        except Exception as e:
              logger.warning(f"There was an error while parsing Draftkings: {e}")

async def scrape_tournaments(tournamentId):
    logger.info(f"Starting task {tournamentId} - Draftkings tournaments")
        #Get all tournaments
    url = constants.draftkings_tournaments.format(id=tournamentId)
    table = db.table("matches_list").select("*").execute()
    table_ids = [item['match_id'] for item in table.data]
    print(url)
    data = {
        'cmd' : 'request.get',
        'url' : url,
        'requestType' : 'request'
    }
    response = await scrape_with_proxy(data, "Draftkings")
    is_valid = verifier(response)
    if is_valid:
        data = json.loads(response['solution']['response'])
        if 'eventGroup' in data and 'events' in data['eventGroup'] and 'offerCategories' in data['eventGroup']:
              markets = data['eventGroup']['offerCategories']
              events = data['eventGroup']['events']
              for event in events:
                    info = {
                          "match_id" : f"{event['eventId']}_dk",
                          "match_name" : f"{event['nameIdentifier']}",
                          "tournament" : f"{event['eventGroupName'].split(' - ')[0]}",
                          "competition" : f"{event['eventGroupName']}",
                          "source" : "Draftkings",
                          "tournament_id" : event['eventGroupId'],
                          "markets_ids" : [item['offerCategoryId'] for item in markets]
                    }

                    if info['match_id'] not in table_ids:
                        response = db.table("matches_list").insert(info).execute()
                        logger.info(response)
                    else:
                        logger.info(f"{info['match_id']} already in table. Skipping.")

    else:
          logger.info(f"Could not finish task {tournamentId} - Draftkings tournaments")

async def scrape_markets():
    table = db.table("matches_list").select("*").match({"source": "Draftkings"}).execute()
    table_tournaments = [[item['tournament_id'], item['markets_ids']] for item in table.data]
 
    merged_list = await remove_duplicates(table_tournaments)
    tasks = []
    for item in merged_list:
        for tournament_id, market_ids in item.items():
            for market_id in market_ids:
                 tasks.append(scrape_market(tournament_id, market_id, constants.draftkings_markets.format(tournament_id=tournament_id, market_id=market_id)))
                ##tasks.append(scrape_market(tournament_id, market_id))
    await asyncio.gather(*tasks)

async def scrape_market(tournament_id, market_id, url):
    logger.info(f"Start of task {tournament_id}/{market_id} - Draftkings")
    print(url)
    data = {
        'cmd' : 'request.get',
        'url' : url,
        'requestType' : 'request'
    }
    response = await scrape_with_proxy(data, "Draftkings")
    is_valid = verifier(response)
    if is_valid:
         if 'solution' in response and 'response' in response['solution']:
              await parse_market_info(response['solution']['response'])
    else:
         logger.info(f"Could not finish task {tournament_id}/{market_id} - Draftkings")
    
    logger.info(f"End of task {tournament_id}/{market_id} - Draftkings")


async def parse_market_info(data):
    try:
         load = json.loads(data)
         if 'eventGroup' in load and 'offerCategories' in load['eventGroup']:
              for category in load['eventGroup']['offerCategories']:
                   if 'offerSubcategoryDescriptors' in category:
                        await marker_sorter(category['offerSubcategoryDescriptors'])
    except Exception as e:
         logger.error(e)
    


#------- Utils
async def remove_duplicates(input_list):
    unique_set = set()
    result = []

    for item in input_list:
        key = item[0]
        values = tuple(item[1])  # Convert list of values to a tuple to make it hashable
        if (key, values) not in unique_set:
            unique_set.add((key, values))
            result.append({key: list(values)})

    return result
    


if __name__ == "__main__":
    asyncio.run(scrape_markets())