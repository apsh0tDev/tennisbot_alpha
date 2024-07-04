import asyncio
import datetime
from db import db
from utils import time_ago
from tabulate import tabulate

async def arbitrage_table():
    repsonse = db.table("arbitrage").select("*").execute()
    data = repsonse.data
    if len(data) > 0:
        header = [
            "Match",
            "Tournament",
            "SportsBooks",
            "Odds",
            "Active Since"
        ]
        body = [header]
        for item in data:
            row = [
                item['match_name'],
                item['tournament'],
                f"{item['odds']['teamA']['sportsbook']} / {item['odds']['teamB']['sportsbook']}",
                f"{item['odds']['teamA']['oddsAmerican']} / {item['odds']['teamB']['oddsAmerican']}",
                time_ago(item['created_at'])
            ]
            body.append(row)

        table = tabulate(body, tablefmt="simple", headers="firstrow", rowalign=("left"))
        code_block = f"""```{table}
        ```"""
        return code_block
    else:
        return None
    
async def get_arbitrages():
    info = {
        "match_name" : "PlayerA vs Player B",
        "tournament" : "WTA",
        "unique_id" : "KMS02L",
        "odds": { 
            "teamA" : {
                "name" : "PlayerA",
                "sportsbook" : "Draftkings",
                "oddsDecimal" : "1.70",
                "oddsAmerican" : "+280"
            },
            "teamB" : {
                "name" : "PlayerB",
                "sportsbook" : "FanDuel",
                "oddsDecimal" : "0.8",
                "oddsAmerican" : "-140"
            }}
        }
    

    db.table("arbitrage").insert(info).execute()

if __name__ == "__main__":
    asyncio.run(get_arbitrages())