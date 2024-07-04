import os
import json
import time
import asyncio
import requests
from rich import print
from loguru import logger
from utils import verifier
from dotenv import load_dotenv
from fp.fp import FreeProxy
from scrapingant_client import ScrapingAntClient

load_dotenv()
key = os.getenv("SCRAPPEY_KEY")
scraping_ant_key = os.getenv("SCRAPING_ANT_TOKEN")

headers = { 'Content-Type' : 'application/json' }
scrappey = f"https://publisher.scrappey.com/api/v1?key={key}"

async def get_data(data):
    options = data
    try:
        response = requests.post(scrappey, headers=headers, json=options)
        return response.json()
    except(ValueError, json.decoder.JSONDecodeError):
        logger.error(f"ERROR")
        logger.error(response)
        return None
    
async def scrape(data, site):
    logger.info(f"Scraping from {site}")

    #Start attempts
    attempts = 0
    while attempts < 2:
        try:
            
            response = await get_data(data=data)
            if response == None:
                attempts += 1
                logger.warning(f"Error getting data - Trying again - ({attempts}/2)")
            else:
                #Check valid response from scrappey
                is_valid = verifier(response)
                if is_valid:
                    return response['solution']['response']
                else:
                    attempts +=1 
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Error scraping live data from {site}: {e}")
            attempts += 1
