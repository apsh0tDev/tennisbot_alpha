import re
import json
import asyncio
from db import db
from rich import print
from thefuzz import fuzz, process
from loguru import logger
from utils import separate_name_and_score, extract_set_and_games
from actions import exists, update, upload

async def market_sorter(event, players, match_name):
    market_name = event['marketName']
    market_type = event['marketType']
    print(market_name, market_type)

    match market_type:
        case "MATCH_BETTING":
            await moneyline(event, players, match_name)
        case "SET_BETTING":
            await set_betting(event, players, match_name)
        case "TO_WIN_1ST_SET":
            await set_winner("Set 1", event, players, match_name)
        case "SET_2_WINNER":
            await set_winner("Set 2", event, players, match_name)
        # case "CORRECT_SCORE_1ST_SET":
        #     await correct_score_set("Set 1", event, players, match_name)
        # case "CORRECT_SCORE_2ND_SET":
        #     await correct_score_set("Set 2", event, players, match_name)
        # case "CORRECT_SCORE_3RD_SET":
        #     await correct_score_set("Set 3", event, players, match_name)
        case "PLAYER_A_TO_WIN_AT_LEAST_1_SET":
            await player_x_to_win_one_set(players[0], event, 0, match_name)
        case "PLAYER_B_TO_WIN_AT_LEAST_1_SET":
            await player_x_to_win_one_set(players[1], event, 1, match_name)
        case "TO_WIN_1ST_SET_AND_WIN_MATCH":
            await to_win_first_set_and_win_match(players=players, event=event, match_name=match_name)
        # case "SET_X_MOST_ACES":
        #     await set_x_aces(event=event, players=players, match_name=match_name, type="MOST")
        # case "SET_X_TOTAL_ACES":
        #     await set_x_aces(event=event, players=players, match_name=match_name, type="TOTAL")
        case "BOTH_PLAYERS_TO_WIN_A_SET_(YES/NO)":
            await both_players_to_win_a_set(event, players, match_name)
        case "OVER_UNDER_TOTAL_SETS":
            await over_under_total_sets(event, match_name)
        case "OVER_UNDER_SET_HANDICAP":
            await over_under_handicap(event, match_name)
        case "SET_X_RACE_TO_Y_GAMES":
            await set_x_race_to_y_games(event, match_name)

async def set_default_info(event, match_name):
    info = {
        "match_id" : event['eventId'],
        "match_name" : match_name,
        "source" : "FanDuel",
        "isOpen" : True if event['marketStatus'] == "OPEN" else False
    }
    return info

    
#---- Popular markets

async def moneyline(event, players, match_name):
    logger.info("Managing MONEYLINE")
    info = await set_default_info(event, match_name)
    info['teamA'] = await moneyline_odds(event['runners'], "teamA")
    info['teamB'] = await moneyline_odds(event['runners'], "teamB")

    to_match = {
        "match_id" : info['match_id'],
        "source" : "FanDuel",
        "match_name" : info['match_name'] 
    }
    to_update = {
        "teamA" : info['teamA'],
        "teamB" : info['teamB'],
        "isOpen" : info['isOpen']
     }
    match_exists = await exists(table="moneyline", to_match=to_match)

    if match_exists:
        response = await update(table="moneyline", info=to_update, to_match=to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload(table="moneyline", info=info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

async def moneyline_odds(odds, team):
    index = 0 if team == "teamA" else 1
    odds = {
        "name" : odds[index]['runnerName'],
        "oddsAmerican" : odds[index]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
        "oddsDecimal" : round(odds[index]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
    }
    return odds

#---- End of Popular markets

#---- Set markets
# Set Betting
async def set_betting(event, players, match_name):
    logger.info("Managing SET BETTING")
    info = await set_default_info(event, match_name)
    info['teamA'] = {
        "name" : players[0],
        "odds" : await get_set_betting_odds(event['runners'], players[0], "teamA")
    }
    info['teamB'] = {
        "name" : players[1],
        "odds" : await get_set_betting_odds(event['runners'], players[1], "teamB")
    }

    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "teamA" : info['teamA'], "teamB" : info['teamB'], "isOpen" : info['isOpen'] }
    match_exists = await exists("set_betting", to_match)
    if match_exists:
        response = await update("set_betting", to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload("set_betting", info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

async def get_set_betting_odds(odds, player, team):
    if team == "teamA":
        names = process.extract(player, [odd['runnerName'] for odd in odds])
        filtered_names = [name for name, score in names if score >= 90]
        two_0 = None
        two_1 = None

        for name in filtered_names:
            for odd in odds:
                if name == odd['runnerName']:
                    if separate_name_and_score(name)[1] == '2-0':
                        two_0 = odd['winRunnerOdds']
                    elif separate_name_and_score(name)[1] == '2-1':
                        two_1 = odd['winRunnerOdds']

        info = {
            "2-0" : {
                "americanOdds" : None if two_0 == None else two_0['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : None if two_0 == None else round(two_0['trueOdds']['decimalOdds']['decimalOdds'], 2)
            },
            "2-1" : {
                "americanOdds" : None if two_1 == None else two_1['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : None if two_1 == None else round(two_1['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }
        }

        return info
    elif team == "teamB":
        names = process.extract(player, [odd['runnerName'] for odd in odds])
        filtered_names = [name for name, score in names if score >= 90]

        one_2 = None
        zero_2 = None

        for name in filtered_names:
            for odd in odds:
                if name == odd['runnerName']:
                    if separate_name_and_score(name)[1] == '2-1':
                        one_2 = odd['winRunnerOdds']
                    elif separate_name_and_score(name)[1] == '2-0':
                        zero_2 = odd['winRunnerOdds']

        info = {
            "1-2" : {
                "americanOdds" : None if one_2 == None else one_2['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : None if one_2 == None else round(one_2['trueOdds']['decimalOdds']['decimalOdds'], 2)
            },
            "0-2" : {
                "americanOdds" : None if zero_2 == None else zero_2['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : None if zero_2 == None else round(zero_2['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }
        }

        return info
    
# Set Winner
async def set_winner(set_name, event, players, match_name):
    print(f"Handling Set Winner - {set_name}")
    info = await set_default_info(event=event, match_name=match_name)
    info['teamA'] = {
        "name" : event['runners'][0]['runnerName'],
        "odds" : {
            "americanOdds" : event['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'],2)
        }
    }
    info['teamB'] = {
        "name" : event['runners'][1]['runnerName'],
        "odds" : {
            "americanOdds" : event['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
        }        
    }

    table_name = "set_one_winner" if set_name == "Set 1" else "set_two_winner"
    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "teamA" : info['teamA'], "teamB" : info['teamB'], "isOpen" : info['isOpen'] }
    match_exists = await exists(table=table_name, to_match=to_match)
    if match_exists:
        response = await update(table_name, to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload(table_name, info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

# Correct Score Set
async def correct_score_set(set_name, event, players, match_name):
    logger.info(f"Managing CORRECT SCORE - {set_name}")
    info = await set_default_info(event, match_name)
    info['teamA'] = {
        "name" : players[0],
        "odds" : await get_correct_score(event['runners'], players[0])
    }
    info['teamB'] = {
        "name" : players[1],
        "odds" : await get_correct_score(event['runners'], players[1])
    }

    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "teamA" : info['teamA'], "teamB" : info['teamB'], "isOpen" : info['isOpen'] }
    match set_name:
        case "Set 1":
            table_name = "correct_score_set_one"
        case "Set 2":
            table_name = "correct_score_set_two"
        case "Set 3":
            table_name = "correct_score_set_three"

    #TODO this is all the same, unify it
    match_exists = await exists(table=table_name, to_match=to_match)
    if match_exists:
        response = await update(table_name, to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload(table_name, info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")
    
async def get_correct_score(odds, player):
    new_odds = {}
    for odd in odds:
        name = odd['runnerName']
        if name == f"{player} 6-0":
            new_odds['6-0'] = {
                "americanOdds": odd['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : round(odd['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }
        elif name == f"{player} 6-1":
            new_odds['6-1'] = {
                "americanOdds": odd['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : round(odd['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }
        elif name == f"{player} 6-2":
            new_odds['6-2'] = {
                "americanOdds": odd['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : round(odd['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }
        elif name == f"{player} 6-3":
            new_odds['6-3'] = {
                "americanOdds": odd['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : round(odd['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
            } 
        elif name == f"{player} 6-4":
            new_odds['6-4'] = {
                "americanOdds": odd['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : round(odd['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }
        elif name == f"{player} 7-5":
            new_odds['7-5'] = {
                "americanOdds": odd['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : round(odd['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }
        elif name == f"{player} 7-6":
            new_odds['7-6'] = {
                "americanOdds": odd['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
                "decimalOdds" : round(odd['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
            }  

    return new_odds

        
# Player to Win at least one set
async def player_x_to_win_one_set(player, event, player_num, match_name):
    logger.info(f"Managing PLAYER TO WIN AT LEAST ONE SET")
    info = await set_default_info(event=event, match_name=match_name)
    info['player_num'] = player_num
    info['odds'] = {
        "team/player" : player,
        "YES" : {
            "americanOdds" : event['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'] or None,
            "decimalOdds" : round(event['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2) or None
        },
        "NO"  :  {
            "americanOdds" : event['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'] or None,
            "decimalOdds" : round(event['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2) or None          
        }   
    }
    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { 'odds' : info['odds'], 'isOpen': info['isOpen'] }

    match_exists = await exists(table="player_to_win_at_least_one_set", to_match=to_match)
    if match_exists:
        response = await update("player_to_win_at_least_one_set", to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload("player_to_win_at_least_one_set", info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

# To Win first set and win match
async def to_win_first_set_and_win_match(event, players, match_name):
    logger.info(f"Managing TO WIN FIRST SET AND WIN MATCH")
    info = await set_default_info(event=event, match_name=match_name)
    info['teamA'] = {
        "name" : players[0],
        "odds" : {
            "status" : event['runners'][0]['runnerStatus'],
            "americanOdds" : event['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
        }
    }
    info['teamB'] = {
        "name" : players[1],
        "odds" : {
            "status" : event['runners'][1]['runnerStatus'],
            "americanOdds" : event['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
        }
    }

    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "teamA" : info['teamA'], "teamB" : info['teamB'], "isOpen" : info['isOpen'] }
    match_exists = await exists(table="player_to_win_first_set_and_match", to_match=to_match)
    if match_exists:
        response = await update("player_to_win_first_set_and_match", to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload("player_to_win_first_set_and_match", info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

# Set X Aces - Most - Total
async def set_x_aces(event, players, match_name, type):
    logger.info(f"Managing SET X ACES")
    info = await set_default_info(event=event, match_name=match_name)
    info['teamA'] = {
        "name" : players[0],
        "odds" : {
            "americanOdds" : event['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
        }
    }
    info['teamB'] = {
        "name" : players[1],
        "odds" : {
            "americanOdds" : event['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
        }
    }

    table = "set_x_total_aces" if type == "TOTAL" else "set_x_most_aces"
    info['set'] = get_set(event['marketName'])

    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "teamA" : info['teamA'], "teamB" : info['teamB'], "isOpen" : info['isOpen'] }
    match_exists = await exists(table=table, to_match=to_match)
    if match_exists:
        response = await update(table, to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload(table, info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

def get_set(description):
    match = re.search(r'(Set 2)', description)
    if match:
        return match.group(1).strip()
    return None

# Both players to win a set
async def both_players_to_win_a_set(event, players, match_name):
    logger.info(f"Managing BOTH PLAYERS TO WIN A SET")
    info = await set_default_info(event, match_name)
    info['YES'] = {
            "americanOdds" : event['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
    }
    info['NO'] = {
            "americanOdds" : event['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
    }

    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "YES" : info['YES'], "NO": info['NO'], "isOpen" : info['isOpen'] }
    await db_actions(to_match=to_match, to_update=to_update, table_name="both_players_to_win_a_set", info=info)

# Over under total sets
async def over_under_total_sets(event, match_name):
    info = await set_default_info(event, match_name)
    info['over'] = {
            "americanOdds" : event['runners'][0]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][0]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)        
    }
    info['under'] = {
            "americanOdds" : event['runners'][1]['winRunnerOdds']['americanDisplayOdds']['americanOdds'],
            "decimalOdds" : round(event['runners'][1]['winRunnerOdds']['trueOdds']['decimalOdds']['decimalOdds'], 2)
    }
    info['points'] = re.search(r'\d+\.\d+', event['marketName']).group()
    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "over" : info['over'], "under": info['under'], "isOpen" : info['isOpen'] }

    await db_actions(to_match=to_match, to_update=to_update, table_name="over_under_total_sets", info=info)

# Over under handicap - Set Spread
async def over_under_handicap(event, match_name):
    logger.info("Managing OVER UNDER HANDICAP")
    info = await set_default_info(event, match_name)
    info['teamA'] = {
        "value" : event['runners'][0]['runnerName'],
        "odds" :  odds_default(event['runners'], 0)
    }
    info['teamB'] = {
        "value" : event['runners'][1]['runnerName'],
        "odds" : odds_default(event['runners'], 1)
    }
    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel"}
    to_update = { "teamA" : info['teamA'], "teamB": info['teamB'], "isOpen" : info['isOpen'] }
    await db_actions(to_match=to_match, to_update=to_update, table_name="set_spread", info=info)

# Set X race to Y games=
async def set_x_race_to_y_games(event, match_name):
    info = await set_default_info(event, match_name)
    info['teamA'] = {
        "name" : event['runners'][0]['runnerName'],
        "odds" : odds_default(event['runners'], 0)
    }
    info['teamB'] = {
        "name" : event['runners'][1]['runnerName'],
        "odds" : odds_default(event['runners'], 1)
    }
    set_number, game_number = extract_set_and_games(event['marketName'])
    info['set_number'] = set_number
    info['game_number'] = game_number
    info['market_full_name'] = event['marketName']

    to_match = {"match_id" : info['match_id'], "match_name" : info['match_name'], "source" : "FanDuel", "market_full_name": info['market_full_name']}
    to_update = { "teamA" : info['teamA'], "teamB": info['teamB'], "isOpen" : info['isOpen'] }

    await db_actions(to_match=to_match, to_update=to_update, table_name="set_x_to_win_y_games", info=info)
    
#---- End of Set markets

#-------- Uploaders
async def db_actions(to_match, to_update, table_name, info):
    match_exists = await exists(table=table_name, to_match=to_match)
    if match_exists:
        response = await update(table_name, to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload(table_name, info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

# ------- Utils

def odds_default(odds, order):
    win_runner_odds = odds[order].get('winRunnerOdds')
    
    if win_runner_odds:
        american_odds = win_runner_odds.get('americanDisplayOdds', {}).get('americanOdds')
        decimal_odds = win_runner_odds.get('trueOdds', {}).get('decimalOdds', {}).get('decimalOdds')
        if decimal_odds is not None:
            decimal_odds = round(decimal_odds, 2)
    else:
        american_odds = None
        decimal_odds = None

    return {
        "americanOdds": american_odds,
        "decimalOdds": decimal_odds
    }

async def search(table, to_match):
    response = db.table(table_name=table).select("*").match(to_match).execute()
    if len(response.data) > 0:
        return True 
    return False

async def post_match(table, info):
    response = db.table(table_name=table).insert(info).execute()
    logger.info(response)

async def update_match(table, info, to_match):
    response = db.table(table_name=table).update(info).match(to_match).execute()
    logger.info(response)