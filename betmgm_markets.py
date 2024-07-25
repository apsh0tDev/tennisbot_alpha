from db import db
from rich import print
from loguru import logger
from actions import exists, update, upload


async def market_sorter(game, match_name, match_id, match_players):
    #print(game)
    market_name = game['name']['value']
    print(market_name)
    match market_name:
        case "Match Winner":
            await handle_match_winner(data=game, id=match_id, match_name=match_name, players=match_players)
        case "Set Betting":
            await handle_set_betting(data=game, id=match_id, match_name=match_name, match_players=match_players)
        case "Set 1 Winner":
            await handle_set_x_winner(data=game, id=match_id, match_name=match_name, match_players=match_players)
        case "Set 2 Winner":
            await handle_set_x_winner(data=game, id=match_id, match_name=match_name, match_players=match_players)
        case "Player 1 to win at least 1 set":
            await handle_player_x_to_win_one_set(data=game, id=match_id, match_name=match_name, match_players=match_players, player_num=0)
        case "Player 2 to win at least 1 set":
            await handle_player_x_to_win_one_set(data=game, id=match_id, match_name=match_name, match_players=match_players, player_num=1)
        case "Correct Score - Set 1":
            await handle_correct_score_set_one(data=game, id=match_id, match_name=match_name, match_players=match_players)
        case "Who will win the match (set spread)?":
            await handle_set_spread(data=game, id=match_id, match_name=match_name, match_players=match_players)
        case "Who will win the most games in the match? (player spread)":
            await handle_player_spread(data=game, id=match_id, match_name=match_name, match_players=match_players)

# Match Winner
async def handle_match_winner(data, id, match_name, players):
    info = await set_default_info(data, id, match_name, "BetMGM", players)
    to_match = { "match_id" : info['match_id'], "source" : "BetMGM", "match_name" : info['match_name'] }
    to_update = {
            "teamA" : info['teamA'],
            "teamB" : info['teamB'],
            "isOpen" : info['isOpen']
        }
    await db_actions(to_match=to_match, to_update=to_update, table_name="match_winner", info=info)


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

    await db_actions(to_match=value_to_match, to_update=to_update, table_name="set_betting", info=info)

# Set One Winner
async def handle_set_x_winner(data, id, match_name, match_players):
    set_name = data['description']
    info = await set_default_info(data, id, match_name, "BetMGM", match_players)
    to_match = { "match_id": info['match_id'], "source": "BetMGM", "match_name": info['match_name'] }
    to_update = { "teamA" : info['teamA'], "teamB": info['teamB'], "isOpen" : info['isOpen'] }
    table = "set_one_winner" if set_name == "Set 1" else "set_two_winner"

    await db_actions(to_match=to_match, to_update=to_update, table_name=table, info=info)

# Player to win at least one set
async def handle_player_x_to_win_one_set(data, id, match_name, match_players, player_num):
    info = {
        "match_id" : id,
        "match_name" : match_name,
        "player_num" : player_num,
        "isOpen" : True if data['visibility'] == "Visible" else False,
        "source" : "BetMGM",
        "odds" : {
            "team/player" : match_players[player_num],
            "YES" : {
                "americanOdds" : data['results'][0]['americanOdds'],
                "decimalOdds" : data['results'][0]['odds']
            },
            "NO" : {
                "americanOdds" : data['results'][1]['americanOdds'],
                "decimalOdds" : data['results'][1]['odds']
            }
        }
    }

    to_match = { "match_id": info['match_id'], "source": "BetMGM", "match_name": info['match_name'], "player_num" : info['player_num'] }
    to_update = { "isOpen" : info['isOpen'], "odds": info['odds'] }
    table = "player_to_win_at_least_one_set"

    await db_actions(to_match=to_match, to_update=to_update, table_name=table, info=info)

# Correct Score - Set X
async def handle_correct_score_set_one(data, id, match_name, match_players):
    scores_teamA = ['6-0', '6-1', '6-2', '6-3', '6-4', '7-5', '7-6']
    scores_teamB = ['0-6', '1-6', '2-6', '3-6', '4-6', '5-7', '6-7']
    set_name = data['name']['value'].split(' - ')[1]
    
    if set_name == "Set 1":
        table = "correct_score_set_one"
    elif set_name == "Set 2":
        table = "correct_score_set_two"
    elif set_name == "Set 3":
        table = "correct_score_set_three"

    info = await set_basic_info(data, id, match_name)
    info['teamA'] = {
        "name" : match_players[0].strip(),
        "odds" : {
                "6-0" : await get_score_info(scores_teamA[0], data['results']),
                "6-1" : await get_score_info(scores_teamA[1], data['results']),
                "6-2" : await get_score_info(scores_teamA[2], data['results']),
                "6-3" : await get_score_info(scores_teamA[3], data['results']),
                "6-4" : await get_score_info(scores_teamA[4], data['results']),
                "7-5" : await get_score_info(scores_teamA[5], data['results']),
                "7-6" : await get_score_info(scores_teamA[6], data['results']),
        }

    }
    info['teamB'] = {
        "name" : match_players[1].strip(),
        "odds" : {
                "6-0" : await get_score_info(scores_teamB[0], data['results']),
                "6-1" : await get_score_info(scores_teamB[1], data['results']),
                "6-2" : await get_score_info(scores_teamB[2], data['results']),
                "6-3" : await get_score_info(scores_teamB[3], data['results']),
                "6-4" : await get_score_info(scores_teamB[4], data['results']),
                "7-5" : await get_score_info(scores_teamB[5], data['results']),
                "7-6" : await get_score_info(scores_teamB[6], data['results']),
        }

    }

    to_match = { "match_id": info['match_id'], "source": "BetMGM", "match_name": info['match_name'] }
    to_update = { "teamA" : info['teamA'], "teamB" : info['teamB'], "isOpen" : info['isOpen'] }
    await db_actions(to_match=to_match, to_update=to_update, table_name=table, info=info)

# Set Spread
async def handle_set_spread(data, id, match_name, match_players):
    #TODO - Check if this has more than 1.5 is currently set to 1.5 only
    
    info = await set_default_info(data, id, match_name, "BetMGM", match_players)
    to_match = { "match_id": info['match_id'], "source": "BetMGM", "match_name": info['match_name'] }
    to_update = { "teamA" : info['teamA'], "teamB" : info['teamB'], "isOpen" : info['isOpen'] }

    #await db_actions(to_match=to_match, to_update=to_update, table_name="set_spread", info=info)

async def handle_player_spread(data, id, match_name, match_players):
    print(data)

#-------- Uploaders
async def db_actions(to_match, to_update, table_name, info):
    match_exists = await exists(table=table_name, to_match=to_match)
    if match_exists:
        response = await update(table_name, to_update, to_match)
        logger.info(f"UPDATE - {info['match_id']} - {response}")
    else:
        response = await upload(table_name, info)
        logger.info(f"UPLOAD - {info['match_id']} - {response}")

# ---- Utils
async def set_basic_info(data, id, match_name):
    info = {
        "match_name" : match_name,
        "match_id" : id,
        "source" : "BetMGM",
        "isOpen" : True if data['visibility'] == "Visible" else False
    }
    return info

async def set_default_info(data, id, match_name, source, players):
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
    
async def get_score_info(score_num, odds):
    for odd in odds:
        if odd['name']['value'] == score_num:
            return {"americanOdds": odd['americanOdds'], "decimalOdds": odd['odds']}

