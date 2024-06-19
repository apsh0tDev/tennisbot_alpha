import json
import asyncio
import constants
from db import db
from rich import print
from loguru import logger
from connection import get_data
from utils import remove_parentheses, verifier


async def scrape_live_events():
    logger.info("Scraping Live events from BetMGM")
    #No need for proxy

    data = {
        'cmd' : 'request.get',
        'url' : constants.schedule_url,
        'requestType' : 'request'
    }
    attempt_count = 1 
    while attempt_count < 3:
        try:
            response = await get_data(data=data)
            if response == None:
                logger.warning(f"Error getting BetMGM Data - Trying again")
                attempt_count += 1
            else:
                #Verifier function
                is_valid = verifier(response) 
                if is_valid:
                    await live_parser(response=response)
                    break
                else:
                    logger.warning(f"Error verifying data - invalid response")
        except Exception as e:
            attempt_count += 1
            logger.warning(f"""Error scraping live data
                           {e}""")
            
async def live_parser(response):
    live_table = db.table("live_matches").select("match_id").execute()
    score_table = db.table("scoreboard").select("match_id").execute()
    live_ids = [item['match_id'] for item in live_table.data]
    score_ids = [item['match_id'] for item in score_table.data]
 
    #TODO get live table and compare
    try:
        load = json.loads(response['solution']['response'])
        if 'widgets' in load and 'payload' in load['widgets'][0] and 'fixtures' in load['widgets'][0]['payload']:
            fixtures = load['widgets'][0]['payload']['fixtures']
            for match in fixtures:
                if match['stage'] == "Live":
                    teamA = f"{remove_parentheses(match['participants'][0]['name']['value']) if len(match['participants']) > 0 else "Unknown"}"
                    teamB = f"{remove_parentheses(match['participants'][1]['name']['value']) if len(match['participants']) > 1 else "Unknown"}"

                    match_info = {
                        "match_id" : match['id'],
                        "match_name" : match['name']['value'],
                        "tournament" : match['tournament']['name']['value'],
                        "tournament_display_name" : match['competition']['name']['value'],
                        "date" : match['startDate'],
                        "teamA" : teamA.strip(),
                        "teamB" : teamB.strip(),
                        "status" : match['stage']
                        }
                    
                    score_info = {
                        "match_id" : match['id'],
                        "period" : match['scoreboard']['period'],
                        "teamA" : [item for item in [match['scoreboard']['setsValues']['player1']]],
                        "teamB" : [item for item in [match['scoreboard']['setsValues']['player2']]]
                    }

                    #Post into live matches table
                    if match['id'] not in live_ids:
                        await post_match(match_info)

                    #Post into score table, if it exist, update score
                    if match['id'] not in score_ids:
                        await post_scores(score_info)
                    else:
                        await update_scores(score_info)

    except Exception as e:
        logger.warning(f"There was an Error while parsing the schedule: {e}")

async def post_match(match):
    response = db.table("live_matches").insert(match).execute()
    logger.info(response)

async def post_scores(match):
    response = db.table("scoreboard").insert(match).execute()
    logger.info(response)

async def update_scores(match):
    response = db.table("scoreboard").update({'teamA': match['teamA'], 'teamB': match['teamB']}).eq('match_id', match['match_id']).execute()
    logger.info(response)

#----- For discord bot
async def get_live_matches():
    live_matches = db.table("live_matches").select("*").execute()
    scoreboard = db.table("scoreboard").select("*").execute()
    
    if len(live_matches.data) > 0 and len(scoreboard.data) > 0:
        formatted = await format_live_matches(data=live_matches.data, scores=scoreboard.data)

#Formats the live data and returns a discord-friendly message
async def format_live_matches(data, scores):
    logger.info("Formatting live table for discord")

    #Group by event
    group = await live_merger(data=data, scores=scores)
    print(group)

async def live_merger(data, scores):
    logger.info("Merging events")
    print(scores)
    merged_list = []
    for entry in data:
        tournament_exists = False
        info = {
            "match_name" : entry['match_name'],
            "teamA" : entry['teamA'],
            "teamB" : entry['teamB'],
        }

        for item in merged_list:
            if item['tournament'] == entry['tournament']:
                tournament_exists = True
                item['events'].append(info)
                break

        if not tournament_exists:
            logger.info(f"{entry['tournament']} not in list, adding...")
            merged_list.append({'tournament' : entry['tournament'], 'events' : [info]})
        else:
            logger.info(f"{entry['tournament']} already in list, adding events...")
    return merged_list


if __name__ == "__main__":
    asyncio.run(get_live_matches())