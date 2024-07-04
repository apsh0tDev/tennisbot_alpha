from db import db
from rich import print
from utils import remove_after_comma
from loguru import logger

def set_default_info(data, id, tournament, match_name, source):
    info = {
    "match_name" : match_name,
    "match_id" : id,
    "source" : source,
    "tournament" : tournament,
    "teamA" : {
        "name" : data['results'][0]['name']['value'],
        "odds" : data['results'][0]['odds'],
        "americanOdds" : data['results'][0]['americanOdds']
    },
    "teamB" : {
        "name" : data['results'][1]['name']['value'],
        "odds" : data['results'][1]['odds'],
        "americanOdds" : data['results'][1]['americanOdds']
    }
    }
    return info

def handle_match_winner(data, id, tournament, match_name, source):
    update = False
    info = set_default_info(data, id, tournament, match_name, source)

    if update:
        response = db.table("match_winner").update({"teamA": info["teamA"], "teamB": info['teamB']}).match({'match_id': info['match_id'], "match_name": info['match_name']}).execute()
        logger.info(response)
    else:
        response = db.table("match_winner").insert(info).execute()
        logger.info(response)

def handle_set_one_winner(data, id, tournament, match_name, source):
    update = False
    print ("Handle set one winner")
    info = set_default_info(data, id, tournament, match_name, source)

    if update:
        response = db.table("set_one_winner").update({"teamA": info["teamA"], "teamB": info['teamB']}).match({'match_id': info['match_id'], "match_name": info['match_name']}).execute()
        logger.info(response)
    else:
        response = db.table("set_one_winner").insert(info).execute()
        logger.info(response)

def handle_set(data, id, tournament, match_name, source):
    global set_table
    game_name = data['name']['value']
    game_v = game_name.split(',')
    info = set_default_info(data, id, tournament, match_name, source)
    info['current_game'] = game_v[0]
    current_set = game_v[1].strip()
    set_table = ''

    match current_set:
        case "Set 1":
            set_table = "set_one"
        case "Set 2":
            set_table = "set_two"
        case "Set 3":
            set_table = "set_three"
        case "Set 4":
            set_table = "set_four"
        case "Set 5":
            set_table = "set_five"

    search = db.table(set_table).select("*").match({'match_id': info['match_id'], 'current_game' : info['current_game']}).execute()
    if len(search.data) == 0:
        response = db.table(set_table).insert(info).execute()
        logger.info(f"Uploading {response}")
    else:
        response = db.table(set_table).update({ "teamA" : info['teamA'], "teamB" : info["teamB"]}).match({"match_id" : info['match_id'], "current_game": info['current_game']}).execute()
        logger.info(f"Updating {response}")