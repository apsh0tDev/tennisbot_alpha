from db import db
from rich import print

def handle_match_winner(data, id, tournament, match_name, source, update):
    print("Handle match winner")
    print(match_name)
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

    if update:
        db.table("match_winner").update({"teamA": info["teamA"], "teamB": info['teamB']}).match({'match_id': info['match_id'], "match_name": info['match_name']}).execute()
    else:
        db.table("match_winner").insert(info).execute()