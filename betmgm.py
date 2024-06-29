import json
import asyncio
import constants
from rich import print
from loguru import logger
from connection import scrape
import markets

async def scrape_data():
    data = {
        'cmd' : 'request.get',
        'url' : constants.schedule_url,
        'requestType' : 'request'
    }

    response = await scrape(data, "BetMGM", 3)
    try:
        load = json.loads(response)
        if 'widgets' in load and 'payload' in load['widgets'][0] and 'fixtures' in load['widgets'][0]['payload']:
            fixtures = load['widgets'][0]['payload']['fixtures']

            for match in fixtures:
                print(match['name']['value'])
                for game in match['games']:
                    switcher(game=game, id=match['id'], tournament=match['tournament']['name']['value'], match_name=match['name']['value'])
                    

    except Exception as e:
        logger.warning(f"There was an Error while parsing BetMGM: {e}")

def switcher(game, id, match_name, tournament):
    name = game['name']['value']
    match name:
        case "Match Winner":
            markets.handle_match_winner(game, id, tournament,  match_name, "BetMGM", True)
        case "Set 1 Winner":
            markets.handle_set_one_winner(game, id, tournament, match_name, "BetMGM", False)

if __name__ == "__main__":
    asyncio.run(scrape_data())