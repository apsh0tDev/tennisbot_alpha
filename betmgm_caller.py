import json
import asyncio
import constants
from db import db
from rich import print
from loguru import logger
from utils import verifier
from connection import scrape_simple, scrape

#General call - Every 20 minutes - Gathers all matches in one place
async def scrape_data():
    table = db.table("matches_list").select("match_id").execute()
    ids = [item['match_id'] for item in table.data]
    data = {
        'cmd' : 'request.get',
        'url' : constants.schedule_url,
        'requestType' : 'request'
    }

    response = await scrape(data, "BetMGM")

    try:
        load = json.loads(response)
        if 'widgets' in load and 'payload' in load['widgets'][0] and 'fixtures' in load['widgets'][0]['payload']:
            fixtures = load['widgets'][0]['payload']['fixtures']
            for match in fixtures:
                if match['stage'] == "Live":
                    info = {
                        "match_name" : match['name']['value'],
                        "match_id" : match['id'],
                        "tournament" : match['tournament']['name']['value'],
                        "competition" : match['competition']['name']['value'],
                        "source" : "BetMGM"
                    }

                    if info['match_id'] not in ids:
                        response = db.table("matches_list").insert(info).execute()
                        logger.info(response)
                    else:
                        logger.info(f"{info['match_id']} already in table. Skipping.")

    except Exception as e:
        logger.error(f"There was an Error while parsing BetMGM: {e}")

#Get all markets by event
async def scrape_event(id):
    logger.info(f"Starting task {id}")
    data = {
        'cmd' : 'request.get',
        'url' : constants.schedule_url,
        'requestType' : 'request'
    }
    response = await scrape_simple(data, "BetMGM")
    is_valid = verifier(response)
    print(is_valid)
    logger.info(f"Ending task {id}")

if __name__ == "__main__":
    asyncio.run(scrape_data())