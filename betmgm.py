import json
import markets
import asyncio
import constants
from db import db
from rich import print
from thefuzz import fuzz
from loguru import logger
from connection import scrape

async def scrape_data():
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
                    for game in match['games']:
                        switcher(game=game, id=match['id'], tournament=match['tournament']['name']['value'], match_name=match['name']['value'])
                    

    except Exception as e:
        logger.warning(f"There was an Error while parsing BetMGM: {e}")

def switcher(game, id, match_name, tournament):
    name = game['name']['value']

    set_one_name = "Game X Winner, Set 1"
    set_two_name = "Game X Winner, Set 2"
    set_three_name = "Game X Winner, Set 3"
    set_four_name = "Game X Winner, Set 4"
    set_five_name = "Game X Winner, Set 5"

    match name:
        case "Set 1 Winner":
            markets.handle_set_one_winner(game, id, tournament, match_name, "BetMGM")

    #Using fuzz radio for game winner
    ratios = [set_one_name, set_two_name, set_three_name, set_four_name, set_five_name]
    for r in ratios:
        fuzz_ratio = fuzz.ratio(name, r)
        if fuzz_ratio >= 95:
            markets.handle_set(data=game, id=id, tournament=tournament, match_name=match_name, source="BetMGM")

if __name__ == "__main__":
    asyncio.run(scrape_data())