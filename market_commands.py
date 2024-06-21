import json
from rich import print
from db import db
from tabulate import tabulate, SEPARATING_LINE

#------ Match winner
async def get_match_winner():
    match_winner = db.table("match_winner").select("*").execute()
    response = await parse_match_winner(match_winner.data)
    return response

async def parse_match_winner(data):
    print("Parsing match winner")
 
    chunks = [data[i:i + 5] for i in range(0, len(data), 5)]
    chunks_array = []
    
    for chunk in chunks:
        header = [
            "**",
            "Players",
            "BetMGM",
            "Draftkings",
            "FanDuel"
        ]
        body = [header]
        
        for entry in chunk:
            row_A = [
                f"{entry['tournament']}",
                f"{entry['teamA']['name']}",
                f"{entry['teamA']['americanOdds']}",
                f" ",
                f" "
            ]

            row_B = [
                f" ",
                f"{entry['teamB']['name']}",
                f"{entry['teamB']['americanOdds']}",
                f" ",
                f" "
            ]

            body.append(row_A)
            body.append(row_B)
            body.append(["-" * len(column) for column in header])  # Assuming this is your SEPARATING_LINE
        
        table = tabulate(body, headers="firstrow", tablefmt="simple")
        print(table)
        chunks_array.append(table)
    
    return chunks_array
    
        

        