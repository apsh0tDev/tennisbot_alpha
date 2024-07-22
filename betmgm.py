import json
import asyncio
import constants
import betmgm_markets
from db import db
from rich import print
from loguru import logger
from utils import verifier, format_match_name, remove_parentheses
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
                #if match['stage'] == "Live":
                    info = {
                        "match_name" : match['name']['value'],
                        "match_id" : match['id'],
                        "tournament" : match['tournament']['name']['value'],
                        "competition" : match['competition']['name']['value'],
                        "source" : "BetMGM",
                    }

                    if info['match_id'] not in ids:
                        response = db.table("matches_list").insert(info).execute()
                        logger.info(response)
                    else:
                        logger.info(f"{info['match_id']} already in table. Skipping.")

    except Exception as e:
        logger.error(f"There was an Error while parsing BetMGM: {e}")

#Get all markets by event
async def scrape_events():
    table = db.table("matches_list").select("*").match({"source" : "BetMGM"}).execute()
    tasks = []
    if len(table.data) > 0:
        for task in table.data:
            tasks.append(scrape_event(task['match_id']))
    
    await asyncio.gather(*tasks)

async def scrape_event(id):
    logger.info(f"Starting task {id} - BetMGM")
    try:
        url = constants.schedule_event.format(id=id)
        data = {
            'cmd' : 'request.get',
            'url' : url,
            'requestType' : 'request'
        }
        response = await scrape_simple(data, "BetMGM")
        #This is a simple scrape, it doesn't use get_data() directly, so it needs to use the verifier
        is_valid = verifier(response)
        if is_valid:
            if 'solution' in response and 'response' in response['solution']:
                res = json.loads(response['solution']['response'])

                # Separate the markets
                if 'fixture' in res and 'games' in res['fixture']:
                    match_name = format_match_name(res['fixture']['name']['value'])
                    match_id = res['fixture']['id']
                    games = res['fixture']['games']
                    match_players = [ remove_parentheses(res['fixture']['participants'][0]['name']['value']), remove_parentheses(res['fixture']['participants'][1]['name']['value'])]
                    tasks = []
                    for game in games:
                        tasks.append(market_handler(game, match_name, match_id, match_players))
                    await asyncio.gather(*tasks)

            logger.info(f"Ending task {id} - BetMGM")
        else:
            raise Exception("Response not valid")
    except Exception as e:
        logger.error(f"Could not finish task {id} - BetMGM")
        logger.error(e)

async def market_handler(game, match_name, match_id, match_players):
    market_name = game['name']['value']
    print(market_name)
    game['match_name'] = match_name
    match market_name:
        case "Match Winner":
            await betmgm_markets.handle_match_winner(game, match_id, match_name, match_players)
        case "Set Betting":
            #TODO finish this market
            await betmgm_markets.handle_set_betting(game, match_id, match_name, match_players)
        case "Set 1 Winner":
            await betmgm_markets.handle_set_one_winner(game, match_id, match_name, match_players)
        case "Set 2 Winner":
             await betmgm_markets.handle_set_two_winner(game, match_id, match_name, match_players)
if __name__ == "__main__":
    asyncio.run(scrape_events())