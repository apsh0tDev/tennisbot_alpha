from db import db
from rich import print
from loguru import logger


def handle_set_winner(eventName, tournament, marketName, market):
    info = {
        "match_id" : market['eventId'],
        "match_name" : eventName,
        "tournament" : tournament,
        "source" : "FanDuel",
        "teamA" : {
        "name" : market['runners'][0]['runnerName'],
        "oddsAmerican" : market['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
        "odds" : market['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds']
        },
        "teamB" : {
            "name" : market['runners'][1]['runnerName'],
            "oddsAmerican" : market['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "odds" : market['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds']
        }
    }
    
    print(info)

    if marketName == "Set 1 Winner":
       table_name = "set_one_winner"
    elif marketName == "Set 2 Winner":
       table_name = "set_two_winner"

    search = db.table(table_name).select("match_id").eq("match_id", info['match_id']).execute()
    if len(search.data) > 0:
       response = db.table(table_name).update({"teamA": info['teamA'], "teamB": info['teamB']}).eq("match_id", info['match_id']).execute()
       logger.info(f"Updating: {response}")
    else:
       response = db.table(table_name).insert(info).execute()
       logger.info(f"Uploading: {response}")
        