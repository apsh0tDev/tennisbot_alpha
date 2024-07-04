import json
import time
import asyncio
from db import db
from rich import print
from thefuzz import fuzz
from loguru import logger
from notifier import notification

async def get_moneyline():
    logger.info("ARBITRAGE CALCULATOR")
    moneyline_table = db.table("moneyline").select("*").execute()
    
    matches = []
    draftkings_matches = []
    fanduel_matches = []
    for match in moneyline_table.data:
        if match['source'] == "Draftkings":
            draftkings_matches.append(match)
        elif match['source'] == "FanDuel":
            fanduel_matches.append(match)

    print("FANDUEL MATCHES:")
    print(fanduel_matches)

    print("DRAFTKINGS MATCHES:")
    print(draftkings_matches)

    for match in fanduel_matches:
        for match_2 in draftkings_matches:
            dk_match = match_2['match_name']
            fd_match = match['match_name']

            fuzz_ratio = fuzz.token_sort_ratio(dk_match, fd_match)
            if fuzz_ratio >= 81:
                print(f"Found a match! {dk_match} AND {fd_match}")
                new_match = {
                    "match_name" : fd_match,
                    "tournament" : match['tournament'],
                    "teamA" : {
                        "Draftkings" : { "oddsDecimal" : match_2['teamA']['oddsDecimal'] },
                        "FanDuel" : { "oddsDecimal" : match['teamA']['oddsDecimal'] }
                    },
                    "teamB" : {
                        "Draftkings" : { "oddsDecimal" : match_2['teamB']['oddsDecimal'] },
                        "FanDuel" : { "oddsDecimal" : match['teamB']['oddsDecimal'] }
                    }
                }
                matches.append(new_match)
    
    print(matches)
    await calculate_arbitrage(matches)

async def calculate_arbitrage(matches):
    for match in matches:
        draftkings_teamA_odds = match['teamA']['Draftkings']['oddsDecimal']
        draftkings_teamB_odds = match['teamB']['Draftkings']['oddsDecimal']
        fanduel_teamA_odds = match['teamA']['FanDuel']['oddsDecimal']
        fanduel_teamB_odds = match['teamB']['FanDuel']['oddsDecimal']



        best_odds_teamA = max(draftkings_teamA_odds, fanduel_teamA_odds)
        best_odds_teamB = max(draftkings_teamB_odds, fanduel_teamB_odds)

        arbitrage_percentage = (1 / best_odds_teamA) + (1 / best_odds_teamB)
        if arbitrage_percentage < 1:

            message = f"""
            
                **Arbitrage Found!**

                `Match` = {match['match_name']}
                `Books` = Draftkings/FanDuel
                `Odds` = {round(best_odds_teamA, 2)} | {round(best_odds_teamB, 2)}
                `Market` = Moneyline

                ------------------
                _Please note: results are subject to change._
            """
            
            notification(message=message)
        time.sleep(2)


if __name__ == "__main__":
    asyncio.run(get_moneyline())