import json
import asyncio
import constants
import betmgm
import fanduel
import draftkings_caller
from db import db
from rich import print
from loguru import logger
from connection import scrape

"""def get_events():
    return db.table("matches_list").select("*").execute()

events = get_events()

async def call_events():
    ids = [item['match_id'] for item in events.data]
    print(ids)
    tasks = [scrape_event(id=match) for match in ids]
    
    await asyncio.gather(*tasks)"""

def get_events():
    return db.table("matches_list").select("*").execute()

events = get_events()

async def call_events():
    fanduel_ids = [item['match_id'] for item in events.data if item['source'] == "FanDuel"]
    betmgm_ids = [item['match_id'] for item in events.data if item['source'] == "BetMGM"]
    draftkings_ids = [item['match_id'] for item in events.data if item['source'] == "DraftKings"]
    #TODO Draftkings IDS
    
    tasks_one = [betmgm.scrape_event(id=match) for match in betmgm_ids]
    tasks_two = [fanduel_caller.scrape_event(id=match) for match in fanduel_ids]
    tasks_three = [draftkings_caller.scrape_event(id=match) for match in draftkings_ids]

    tasks = [*tasks_two]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(call_events())