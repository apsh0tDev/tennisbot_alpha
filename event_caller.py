import json
import asyncio
import constants
from db import db
from rich import print
from loguru import logger
from connection import scrape
from betmgm_caller import scrape_event

async def get_events():
    return db.table("matches_list").select("*").execute()

async def call_events():
    ids = [16025255, 16041962, 16025246, 16025251]
    tasks = [scrape_event(id=match) for match in ids]
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(call_events())