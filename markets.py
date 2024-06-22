from db import db
from rich import print

def set_default_info(data, id, tournament, match_name, source, update):
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

def handle_match_winner(data, id, tournament, match_name, source, update):
    info = set_default_info(data, id, tournament, match_name, source, update)

    if update:
        db.table("match_winner").update({"teamA": info["teamA"], "teamB": info['teamB']}).match({'match_id': info['match_id'], "match_name": info['match_name']}).execute()
    else:
        db.table("match_winner").insert(info).execute()

def handle_set_one_winner(data, id, tournament, match_name, source, update):
    print ("Handle set one winner")
    info = set_default_info(data, id, tournament, match_name, source, update)

    if update:
        db.table("set_one_winner").update({"teamA": info["teamA"], "teamB": info['teamB']}).match({'match_id': info['match_id'], "match_name": info['match_name']}).execute()
    else:
        db.table("set_one_winner").insert(info).execute()