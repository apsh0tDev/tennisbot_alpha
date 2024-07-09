import json
import asyncio
import constants
from rich import print
from loguru import logger
from connection import scrape
from fanduel_markets import handle_set_winner

async def scrape_data():
    data = {
        'cmd' : 'request.get',
        'url' : constants.fanduel_url,
        'requestType' : 'request'
    }

    response = await scrape(data, "FanDuel")
    try:
        load = json.loads(response)
        events = []
        if 'attachments' in load and 'markets' in load['attachments']:
            markets = load['attachments']['markets']
            list_of_dicts = [{key: value} for key, value in markets.items()]

            for market in list_of_dicts:
                for key in market:
                    events.append(market[key])
            
            logger.info("Handling markets")
            await handle_markets(events)

    except Exception as e:
        logger.error(e)

async def handle_markets(events):

    calls = []

    #for event in events:
    if events[0]['inPlay'] == False:
        calls.append(get_event(events[0]['eventId'], events[0]['competitionId']))

    await asyncio.gather(*calls)

    """if 'attachments' in load and 'markets' in load['attachments']:
        markets = load['attachments']['markets']
        list_of_dicts = [{key: value} for key, value in markets.items()]
        event_name = load['attachments']['events'][id]['name']
        tournament = load['attachments']['competitions'][tournamentId]['name']
        for market in list_of_dicts:
            for key in market:
                marketName = market[key]['marketName']
                if marketName == 'Set 1 Winner' or marketName == 'Set 2 Winner':
                    handle_set_winner(event_name, tournament, marketName, market[key])"""

async def get_event(eventId, tournamentId):
    data = {
        'cmd' : 'request.get',
        'url' : f"https://sbapi.ny.sportsbook.fanduel.com/api/event-page?_ak=FhMFpcPWXMeyZxOx&eventId={eventId}&tab=all&useCombinedTouchdownsVirtualMarket=false&usePulse=false&useQuickBets=false",
        'requestType' : 'request'
    }
    response = await scrape(data, "FanDuel")
    load = json.loads(response)
    if 'attachments' in load and 'markets' in load['attachments']:
        markets = load['attachments']['markets']
        if len(markets) > 0:
            list_of_dicts = [{key: value} for key, value in markets.items()]
            event_name = load['attachments']['events'][eventId]['name']
            tournament = load['attachments']['competitions'][tournamentId]['name']
            for market in list_of_dicts:
                for key in market:
                    marketName = market[key]['marketName']
                    if marketName == 'Set 1 Winner' or marketName == 'Set 2 Winner':
                        handle_set_winner(event_name, tournament, marketName, market[key])


if __name__ == "__main__":
    asyncio.run(scrape_data())