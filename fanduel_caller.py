import json
import asyncio
import constants
from db import db
from rich import print
from loguru import logger
from connection import scrape, scrape_with_proxy

async def scrape_data():
    data = {
        'cmd' : 'request.get',
        'url' : constants.fanduel_url,
        'requestType' : 'request'
    }

    response = await scrape(data, "FanDuel")
    try:
        load = json.loads(response)
        
        if 'attachments' in load and 'markets' in load['attachments']:
            #Markets
            markets = load['attachments']['markets']
            list_of_dicts = [{key: value} for key, value in markets.items()]
            for market in list_of_dicts:
                for key in market:
                    if 'inPlay' in market[key] and market[key]['inPlay'] == True:
                        info = {
                            "match_id" : market[key]['eventId'],
                            "match_name" : f"{market[key]['runners'][0]['runnerName']} v {market[key]['runners'][1]['runnerName']}",
                            "source" : "FanDuel"
                        }
                        search = db.table("matches_list").select("*").match({"match_id": info['match_id'], "match_name": info['match_name'], "source": info['source']}).execute()

                        if len(search.data) == 0:
                            res = db.table("matches_list").insert(info).execute()
                            print(res)
                        else:
                            logger.info(f"{info['match_id']} already in table. Skipping")

    except Exception as e:
        logger.info(f"Error Scraping FanDuel - {e}")


async def scrape_event(id):
    logger.info(f"Starting task {id} - Fanduel")
    url = constants.fanduel_event_url.format(id=id)
    data = {
        'cmd' : 'request.get',
        'url' : url,
        'requestType' : 'request'
    }
    response = await scrape_with_proxy(data, "FanDuel")
    print(response)
    

if __name__ == "__main__":
    asyncio.run(scrape_data())