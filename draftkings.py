import json
import asyncio
import constants
from db import db
from rich import print
from thefuzz import fuzz
from loguru import logger
from connection_old import scrape
from db_actions import update, upload


async def scrape_data():
        data = {
        'cmd' : 'request.get',
        'url' : constants.draftkings_url,
        'requestType' : 'request'
        }
        
        response = await scrape(data, "Draftkings", 3)
        try:
                load = json.loads(response)
                if "featuredDisplayGroup" in load and "featuredSubcategories" in load["featuredDisplayGroup"]:
                        subcats = load['featuredDisplayGroup']['featuredSubcategories']
                        event_groups = []

                        for item in subcats[0]['featuredEventGroupSubcategories']:
                                event_groups.append({
                                        "eventGroupId" : item['eventGroupId'],
                                        "eventGroupName" : item['eventGroupName']
                                })
                        
                        await get_moneyline(event_groups)
        except Exception as e:
                logger.warning(f"There was an error while parsing Draftkings: {e}")

async def get_moneyline(data):
        table = db.table("moneyline").select("tournament").execute()
        tournaments_list = [item['tournament'] for item in table.data]
        tournaments = list(set(tournaments_list))
        print(tournaments)
        to_search = []
        logger.info("Finding tournament matches: ")
        for tournament in tournaments:
            for el in data:
                    fuzz_ratio = fuzz.token_sort_ratio(el['eventGroupName'], tournament)
                    if fuzz_ratio >= 79:
                            print(f"Found a match!: {el['eventGroupName']} & {tournament}")
                            to_search.append(el['eventGroupId'])
        logger.info("Finished finding matches")

        if len(to_search) > 0:
              tasks = []
              for item in to_search:
                     options = {
                            'cmd' : 'request.get',
                            'url' : f"https://sportsbook-nash.draftkings.com/sites/US-SB/api/v5/eventgroups/{item}?format=json",
                            'requestType' : 'request'
                     }
                     logger.info(f"Getting info for: {item}")
                     tasks.append(scrape_and_clean(options))

              await asyncio.gather(*tasks)

              
                   
        else:
                logger.info("No matches to retrieve data")

async def scrape_and_clean(options):
    response = await scrape(options, "Draftkings", 3)
    res_load = json.loads(response)
    await clean_moneyline(res_load)

async def clean_moneyline(data):
       logger.info("Cleaning data")
       if 'eventGroup' in data and 'offerCategories' in data['eventGroup']:
              tournament_name = data['eventGroup']['name']
              short = data['eventGroup']['offerCategories'][0]['offerSubcategoryDescriptors']
              if 'offerSubcategory' in short[0] and 'offers' in short[0]['offerSubcategory']:
                     offers = short[0]['offerSubcategory']['offers']
                     for offer in offers:
                            info = {
                                   "tournament" : tournament_name,
                                   "match_id" : f"{offer[0]['eventId']}_df",
                                   "match_name" : f"{offer[0]['outcomes'][0]['participant']} vs {offer[0]['outcomes'][1]['participant']}" or "Unknown",
                                   "teamA" : {
                                          "name" : offer[0]['outcomes'][0]['participant'],
                                          "oddsAmerican" : offer[0]['outcomes'][0]['oddsAmerican'],
                                          "oddsDecimal" : offer[0]['outcomes'][0]['oddsDecimal']
                                   },
                                   "teamB" : {
                                          "name" : offer[0]['outcomes'][1]['participant'],
                                          "oddsAmerican" : offer[0]['outcomes'][1]['oddsAmerican'],
                                          "oddsDecimal" : offer[0]['outcomes'][1]['oddsDecimal']
                                   },
                                   "source" : "Draftkings"
                            }
                            await handle_moneyline(info)
                            
async def handle_moneyline(info):
    table = db.table("moneyline").select("match_id").execute()
    ids = [item['match_id'] for item in table.data]

    print("Handle moneyline")
    #Fix the match id situation
    if info['match_id'] not in ids:
           logger.info("Uploading")
           response = await upload(info, "moneyline")
           logger.info(response)
    else:
           logger.info("Updating")
           to_update = {
                  "teamA" : info['teamA'],
                  "teamB" : info['teamB']
            }
           response = await update(info=to_update, table="moneyline", value=info['match_id'], to_match="match_id")
           logger.info(response)

#--------- For scheduled matches
async def scrape_sch_data():
        data = {
        'cmd' : 'request.get',
        'url' : constants.draftkings_url_scheduled,
        'requestType' : 'request'
        }

        response = await scrape(data, "Draftkings", 3)
        load = json.loads(response)
        tournaments = []
        if 'displayGroupInfos' in load:
               for displayGroup in load['displayGroupInfos']:
                      if displayGroup['displayGroupId'] == '6':
                             for event in displayGroup['eventGroupInfos']:
                                    tournaments.append({
                                           "eventGroupId" : event['eventGroupId'],
                                           "eventGroupName" : event['nameIdentifier']
                                    })


        print(tournaments)   
        await get_moneyline(tournaments)
                            

if __name__ == "__main__":
        asyncio.run(scrape_data())