import json
import constants
import asyncio
from db import db
from rich import print
from loguru import logger
from utils import remove_year
from connection_old import scrape, get_data_with_scraping_ant



async def scrape_data():
        data = {
        'cmd' : 'request.get',
        'url' : constants.fanduel_url,
        'requestType' : 'request'
        }

        response = await scrape(data, "FanDuel", 2)
        try:
            load = json.loads(response)
            events = []
            tournaments = []
            if 'attachments' in load and 'markets' in load['attachments']:
                markets = load['attachments']['markets']
                list_of_dicts = [{key: value} for key, value in markets.items()]
                    
                for market in list_of_dicts:
                    for key in market:
                        #if 'inPlay' in market[key] and market[key]['inPlay'] == True:
                            #logger.info(f"In play: {market[key]['competitionId']} - {market[key]['marketName']}")
                            events.append(market[key])
                    

            if 'attachments' in load and 'competitions' in load['attachments']:
                  competitions = load['attachments']['competitions']
                  list_of_dicts = [{key: value} for key, value in competitions.items()]

                  for competition in list_of_dicts:
                        for key in competition:
                              tournaments.append(competition[key])
                        
            #await get_moneyline(events, tournaments)
            await get_game_markets(events)
            
                                         

        except Exception as e:
                logger.warning(f"There was an Error while parsing Fanduel: {e}")
        
        
#----- Moneyline
async def get_moneyline(data, tournaments):
        moneyline = db.table("moneyline").select("match_id").execute()
        ids = [item['match_id'] for item in moneyline.data]
        if len(data) > 0:
              for element in data:
                    competition_id = element['competitionId']
                    global tournament
                    for item in tournaments:
                        if item['competitionId'] == competition_id:
                                tournament = item['name']
                    info = {
                        "tournament" : remove_year(tournament),
                        "match_id": element['eventId'],
                        "teamA" : {
                                "name" : element['runners'][0]['runnerName'],
                                "oddsAmerican" : element['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                                "oddsDecimal" : element['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds']
                        },
                        "teamB" : {
                                "name" : element['runners'][1]['runnerName'],
                                "oddsAmerican" : element['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                                "oddsDecimal" : element['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds']
                        },
                        "source" : "FanDuel",
                        "match_name" : f"{element['runners'][0]['runnerName']} vs {element['runners'][1]['runnerName']}" 
                    }
                    
                    idstr = f"{info['match_id']}"
                    if idstr not in ids:
                        logger.info(f"{info['match_id']} not in table")
                        await upload(info, "moneyline")
                    else:
                        await update(info, "moneyline", info['match_id'])


        else:
               raise Exception("No events for moneyline")
        
#---- Game markets
async def get_game_markets(data):
    print(data)

        

#---- TODO make this a single thing for all
        
async def upload(info, table):
    response = db.table(table).insert(info).execute()
    logger.info(f"Posting: {response}")

async def update(info, table, id):
      response = db.table(table).update(info).eq('match_id', id).execute()
      logger.info(f"Updating: {response}")



if __name__ == "__main__":
        asyncio.run(scrape_data())