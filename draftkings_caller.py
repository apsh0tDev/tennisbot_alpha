import json 
import asyncio
import constants
from db import db
from rich import print
from thefuzz import fuzz
from loguru import logger
from utils import verifier
from connection import scrape, scrape_with_proxy

async def scrape_data():
    data = {
        'cmd' : 'request.get',
        'url' : constants.draftkings_url,
        'requestType' : 'request'
    }

    response = await scrape(data, "Draftkings")
    search = db.table("matches_list").select("*").execute()
    competitions = list(set([item['competition'] for item in search.data]))
    tasks = []
    try:
        load = json.loads(response)
        if 'featuredDisplayGroup' in load and 'featuredSubcategories' in load['featuredDisplayGroup']:
            #Get tournaments first
            res = load['featuredDisplayGroup']['featuredSubcategories'][0]
            if 'featuredEventGroupSubcategories' in res:
                for eventGroup in res['featuredEventGroupSubcategories']:
                    for item in competitions:
                        print(f"Comparing: {item} and {eventGroup['eventGroupName']}")
                        fuzz_ratio = fuzz.token_sort_ratio(item, eventGroup['eventGroupName'])
                        if fuzz_ratio >= 90:
                            tasks.append(scrape_tournament(eventGroup['eventGroupId']))
    except Exception as e:
        logger.info(f"Error scraping data from Draftkings {e}")

    await asyncio.gather(*tasks)

async def scrape_tournament(id):
    logger.info(f"Starting task {id} - Draftkings - Tournament")
    url = constants.draftkings_tournaments.format(id=id)
    data = {
        'cmd' : 'request.get',
        'url' : url,
        'requestType' : 'request'
    }
    response = await scrape_with_proxy(data, "Draftkings")
    is_valid = verifier(response)
    if is_valid:
        if 'solution' in response and 'response' in response['solution']:
            load = json.loads(response['solution']['response'])
            if 'eventGroup' in load and 'events' in load['eventGroup']:
                events = load['eventGroup']['events']
                for event in events:
                    info = {
                        "match_id" : f"{event['eventId']}_dk",
                        "match_name" : event['name'],
                        "competition" : event['eventGroupName'],
                        "source" : "DraftKings"
                    }

                    search = db.table("matches_list").select("*").match({"match_id" : info['match_id'], "match_name" : info['match_name'], "source": info['source']}).execute()
                    if len(search.data) == 0:
                        response = db.table("matches_list").insert(info).execute()
                        print(response)
                    else:
                        logger.info(f"{info['match_id']} already in table. Skipping")
    else:
        print(f"Add for retry: {id} - Draftkings")
    


if __name__ == "__main__":
    asyncio.run(scrape_data())