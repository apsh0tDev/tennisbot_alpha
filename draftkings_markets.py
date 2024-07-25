import json
import asyncio
from rich import print

async def marker_sorter(event):
    market_name = event[0]['name']
    match market_name:
        case "Moneyline":
            await handle_moneyline(event)

async def handle_moneyline(event):
    if 'offerSubcategory' in event[0] and 'offers' in event[0]['offerSubcategory']:
        offers = event[0]['offerSubcategory']['offers']
        for offer in offers:
            info = await set_default_info(offer)
            

#--- Utils
async def set_default_info(data):
    info = {
        "match_id" : f"{data[0]['eventId']}_dk",
        "source" : "Draftkings",
        "isOpen" : data[0]['isOpen']
    }
    return info

async def set_default_odds(data):
    print(data)
