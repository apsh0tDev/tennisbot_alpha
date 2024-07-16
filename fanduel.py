import json
import asyncio
import constants
from rich import print
from loguru import logger
from utils import verifier
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

        #first let's separate the competitions
        if 'attachments' in load and 'competitions' in load['attachments']:
            competitions = load['attachments']['competitions']

        if 'attachments' in load and 'events' in load['attachments']:
            events = load['attachments']['events']
            
            #first get the key for each event
            event_keys = [key for key in events]
            for key in event_keys:
                event = events[key]
                info = {
                    "match_id" : event['eventId'],
                    "match_name" : event['name'],
                    "competition" : find_competition(event['competitionId'], competitions)
                }

                print(info)
                

    except Exception as e:
        logger.info(f"Error scraping data from Draftkings {e}")


# ------- Utils
def find_competition(id, group):
    group_keys = [key for key in group]
    for key in group_keys:
        if str(id) == key:
            return group[key]['name']


if __name__ == "__main__":
    asyncio.run(scrape_data())