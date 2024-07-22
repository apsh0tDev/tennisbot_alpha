from db import db
from rich import print
from loguru import logger
from actions import exists, update, upload

# ---- Utils

def set_default_info(data, id, match_name, source, players):
    info = {
    "match_name" : match_name,
    "match_id" : id,
    "source" : source,
    "teamA" : {
        "name" : players[0].strip(),
        "odds" : data['results'][0]['odds'],
        "americanOdds" : data['results'][0]['americanOdds']
    },
    "teamB" : {
        "name" : players[1].strip(),
        "odds" : data['results'][1]['odds'],
        "americanOdds" : data['results'][1]['americanOdds']
    },
    "isOpen" : True if data['visibility'] == "Visible" else False
    }

    return info

def get_set_betting_info(bet, data):
    keys = [item['name']['value'] for item in data]

    if bet in keys:
        for odds in data:
            if bet == odds['name']['value']:
                return odds
    else:
        return None

# ---- Handlers

# Match Winner
async def handle_match_winner(data, id, match_name, players):
    info = set_default_info(data, id, match_name, "BetMGM", players)
    to_match = { "match_id" : info['match_id'], "source" : "BetMGM", "match_name" : info['match_name'] }
    match_exists = await exists(table="match_winner", to_match=to_match)
    if match_exists:
        to_change = {
            "teamA" : info['teamA'],
            "teamB" : info['teamB'],
            "isOpen" : info['isOpen']
        }
        res = await update(table="match_winner", info=to_change, to_match=to_match)
        logger.info(f"UPDATE: {id} - {res}")
    else:
        res = await upload(table="match_winner", info=info)
        logger.info(f"UPLOAD: {id} - {res}")

# Set Betting
async def handle_set_betting(data, id, match_name, match_players):
    two_0 = get_set_betting_info("2-0", data['results'])
    two_1 = get_set_betting_info("2-1", data['results'])
    one_2 = get_set_betting_info("1-2", data['results'])
    zero_2 = get_set_betting_info("0-2", data['results'])

    info = {
        "match_name" : match_name,
        "match_id" : id,
        "source" : "BetMGM",
        "teamA" : {
            "name" : match_players[0].strip(),
            "odds" : {
                "2-0" : {
                    "decimalOdds" : None if two_0 == None else two_0['odds'],
                    "americanOdds" : None if two_0 == None else two_0['americanOdds']
                },
                "2-1" : {
                    "decimalOdds" : None if two_1 == None else two_1['odds'],
                    "americanOdds" : None if two_1 == None else two_1['americanOdds']
                }
            }
        },
        "teamB" : {
            "name" : match_players[1].strip(),
            "odds" : {
                "1-2" : {
                    "decimalOdds" : None if one_2 == None else one_2['odds'],
                    "americanOdds" : None if one_2 == None else one_2['americanOdds']
                },
                "0-2" : {
                    "decimalOdds" : None if zero_2 == None else zero_2['odds'],
                    "americanOdds" : None if zero_2 == None else zero_2['americanOdds']
                }
            }
        },
        "isOpen" : True if data['visibility'] == 'Visible' else False
    }
    
    to_update = { "teamA" : info['teamA'], "teamB": info['teamB'], "isOpen" : info['isOpen'] }
    value_to_match = { "match_id" : info['match_id'], "source": "BetMGM", "match_name": info['match_name'] }
    value_exists = await exists("set_betting", value_to_match)
    if value_exists:
        response = await update(table="set_betting", info=to_update, to_match=value_to_match)
        logger.info(f"UPDATE: {id} - {response}")
    else:
        response = await upload(table="set_betting", info=info)
        logger.info(f"UPLOAD: {id} - {response}")

# Set One Winner
async def handle_set_one_winner(data, id, match_name, match_players):
    print("SET ONE WINNER")
    info = set_default_info(data, id, match_name, "BetMGM", match_players)
    
    to_match = { "match_id": info['match_id'], "source": "BetMGM", "match_name": info['match_name'] }
    to_update = { "teamA" : info['teamA'], "teamB": info['teamB'], "isOpen" : info['isOpen'] }

    match_exists = await exists("set_one_winner", to_match)
    if match_exists:
        response = await update(table="set_one_winner", to_match=to_match, info=to_update)
        logger.info(f"UPDATE - {id} - {response}")
        #TODO make a repsonse handler
    else:
        response = await upload(table="set_one_winner", info=info)
        logger.info(f"UPLOAD - {id} - {response}")

# Set One Winner #TODO honestly the same as set one winner - unify them
async def handle_set_two_winner(data, id, match_name, match_players):
    print("SET TWO WINNER")
    info = set_default_info(data, id, match_name, "BetMGM", match_players)
    
    to_match = { "match_id": info['match_id'], "source": "BetMGM", "match_name": info['match_name'] }
    to_update = { "teamA" : info['teamA'], "teamB": info['teamB'], "isOpen" : info['isOpen'] }

    match_exists = await exists("set_two_winner", to_match)
    if match_exists:
        response = await update(table="set_two_winner", to_match=to_match, info=to_update)
        logger.info(f"UPDATE - {id} - {response}")
        #TODO make a repsonse handler
    else:
        response = await upload(table="set_two_winner", info=info)
        logger.info(f"UPLOAD - {id} - {response}")    