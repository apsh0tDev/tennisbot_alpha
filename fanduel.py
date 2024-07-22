import json
import asyncio
import constants
from db import db
from rich import print
from loguru import logger
from utils import verifier, extract_players
from fanduel_markets import market_sorter
from connection import scrape, scrape_with_proxy

# Scrapes the general information - this call occurs every 10 to 15 minutes
# since we just need general market information, event name, players names, etc.
# No scores or odds
async def scrape_data():
    data = {
        'cmd' : 'request.get',
        'url' : constants.fanduel_url,
        'requestType' : 'request'
    }

    response = await scrape(data, "FanDuel")
    #No need for verifier here - the scrape function already does it

    
    try:
        load = json.loads(response)
        #let's break down the response using json loads

        #let's separate the competitions
        if 'attachments' in load and 'competitions' in load['attachments']:
            competitions = load['attachments']['competitions']

        if 'attachments' in load and 'events' in load['attachments']:
            evs = load['attachments']['events']

        #now we need to know if the events are live
        if 'attachments' in load and 'markets' in load['attachments']:
            markets = load['attachments']['markets']
            #get the key for each market

            market_keys = [key for key in markets]
            for key in market_keys:
                if 'inPlay' in markets[key] and markets[key]['inPlay'] == True:
                    event = markets[key]
                    info = {
                        "match_id": event['eventId'],
                        "match_name" : find_value(event['eventId'], evs),
                        "competition" : find_value(event['competitionId'], competitions),
                        "source" : "FanDuel"
                    }

                    #upload it to the database if it doesn't exist first
                    value_exists = search("matches_list", {"match_id": info['match_id'], "source": info['source'], "match_name": info['match_name']})
                    if value_exists:
                        print("exists, skip")
                    else:
                        post_match(table="matches_list", info=info)
              

    except Exception as e:
        logger.info(f"Error scraping data from FanDuel {e}")


#------- Market separation and individual scraping

async def scrape_events():
    table = db.table("matches_list").select("*").match({"source": "FanDuel"}).execute()
    
    ids = [item['match_id'] for item in table.data]

    #scrape each event in parallel
    tasks = []
    for id in ids:
       tasks.append(scrape_event(id))

    await asyncio.gather(*tasks)

async def scrape_event(id):
    logger.info(f"Starting task {id} at FanDuel ")
    url = constants.fanduel_event_url.format(id=id, tab=constants.fanduel_tabs[3]['case'])
    print(url)
    data = {
    'cmd' : 'request.get',
    'url' : url,
    'requestType' : 'request'
    }
    response = await scrape_with_proxy(data, "FanDuel")
    is_valid = verifier(response)
    if is_valid:
        if 'solution' in response and 'response' in response['solution']:
            await parse_event_info(response['solution']['response'])
        logger.info(f"Ending task {id} at FanDuel ")
    else:
        logger.info(f"Error on task {id} at FanDuel ")
        logger.info(response)
        
async def parse_event_info(event):
    try:
        load = json.loads(event)
    
        event_key = [key for key in load['attachments']['events']]
        match_name = load['attachments']['events'][event_key[0]]['name']
        players = extract_players(load['attachments']['events'][event_key[0]]['name'])

        if 'attachments' in load and 'markets' in load['attachments']:
            markets = load['attachments']['markets']
            market_keys = [key for key in markets]
            for key in market_keys:
                market = markets[key]
                await market_sorter(market, players, match_name)

    except Exception as e:
        logger.error(e)
    

#------- End of market separation and individual scraping


# ------- Utils
def find_value(id, group):
    group_keys = [key for key in group]
    for key in group_keys:
        if str(id) == key:
            return group[key]['name']
        
def search(table, to_match):
    response = db.table(table_name=table).select("*").match(to_match).execute()
    if len(response.data) > 0:
        return True 
    return False

def post_match(table, info):
    response = db.table(table_name=table).insert(info).execute()
    logger.info(response)


if __name__ == "__main__":
    asyncio.run(scrape_events())