import json
import asyncio
import constants
from db import db
from rich import print
from loguru import logger
from tabulate import tabulate
from connection_old import get_data
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
            match_ids = []

            for match in fixtures:
                match_ids.append(match['id'])
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
                    elif match['scoreboard']['period'] == "Suspended":
                        print("Match is suspended, don't do anything")
                    else:
                        await update_scores(score_info)

            #clean up 🧹
            setB = set(match_ids)
            removed_elements = []

            filtered = []
            for x in live_ids:
                if x in setB:
                    filtered.append(x)
                else:
                    removed_elements.append(x)

            for item in removed_elements:
                await clean_up(item)


    except Exception as e:
        logger.warning(f"There was an Error while parsing the live matches: {e}")


async def post_match(match):
    db.table("live_matches").insert(match).execute()

async def post_scores(match):
    db.table("scoreboard").insert(match).execute()
    

async def update_scores(match):
    db.table("scoreboard").update({'teamA': match['teamA'], 'teamB': match['teamB'], 'period' : match['period']} ).eq('match_id', match['match_id']).execute()
    
async def clean_up(id):
    response = db.table("live_matches").delete().eq('match_id', id).execute()
    print(response)

#----- For discord bot ------------
async def get_live_matches():
    live_matches = db.table("live_matches").select("*").execute()
    scoreboard = db.table("scoreboard").select("*").execute()
    if len(live_matches.data) > 0 and len(scoreboard.data) > 0:
        print(live_matches.data, scoreboard.data)
        formatted = await format_live_matches(data=live_matches.data, scores=scoreboard.data)
        return formatted
    else:
        return None

#Formats the live data and returns a discord-friendly message
async def format_live_matches(data, scores):
    logger.info("Formatting live table for discord")

    #Group by event
    group = await live_merger(data=data, scores=scores)
    print(group)
    if len(group) > 0:
        for tournament in group:
            formatted = await format_tournament(tournament=tournament)
            table_output = "\n".join(formatted)
            code_block = f"""```
            {table_output}
            ```"""
            return code_block

async def live_merger(data, scores):
    print(data, scores)
    logger.info("Merging events")
    scores_dict = {}

    for score in scores:
        if 'match_id' in score:
            scores_dict[score['match_id']] = score
        else:
            logger.warning(f"Score entry missing 'match_id': {score}")

    merged_list = []
    for entry in data:
        tournament_exists = False
        match_id = entry.get('match_id')
        info = {
            "match_name" : entry['match_name'],
            "teamA" : entry['teamA'],
            "teamB" : entry['teamB'],
        }

        if match_id in scores_dict:
            score = scores_dict[match_id]
            info['teamA_score'] = score['teamA'][0]
            info['teamB_score'] = score['teamB'][0]
            info['period'] = score['period']

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

async def format_tournament(tournament):
    print(f"Formatting live tournament: {tournament['tournament']}")
    formatted_event = []
    #This will be the title
    formatted_event.append(f"{tournament['tournament'].upper()}\n")
   #And this is the list of events
    for match in tournament['events']:
        header = [
                f"{match['period']}",
                "*",
                "1st",
                "2nd",
                "3rd"
                #TODO add optional 4th and 5th set
            ]

        first_row = [
                f"{match['teamA']}",
                "*",
                f"{match['teamA_score'][0]}",
                f"{match['teamA_score'][1]}",
                f"{match['teamA_score'][2]}"
            ]

        second_row = [
                f"{match['teamB']}",
                "*",
                f"{match['teamB_score'][0]}",
                f"{match['teamB_score'][1]}",
                f"{match['teamB_score'][2]}"           
            ]

            #unify the table
        body = [header, first_row, second_row]
        score_table = tabulate(body, tablefmt="simple")
        formatted_event.append(f"{match['match_name']}\n{score_table}\n")

    return formatted_event

if __name__ == "__main__":
    asyncio.run(get_live_matches())