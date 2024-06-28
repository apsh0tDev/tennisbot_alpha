import os
import json
import time
import requests
from rich import print
from loguru import logger
from utils import verifier
from typing import Literal
from dotenv import load_dotenv
from fp.fp import FreeProxy
from scrapingant_client import ScrapingAntClient

load_dotenv()
key = os.getenv("SCRAPPEY_KEY")
provider: Literal["Scrappey", "AnyIP"] = "AnyIP"

headers = { 'Content-Type' : 'application/json' }
scrappey = f"https://publisher.scrappey.com/api/v1?key={key}"

proxy_needed = ["Draftkings"]
client = ScrapingAntClient(token='08e2512b9b8540e58e420b21eacc810f')

#TODO add banned validation
async def get_data(data):
    options = data
    try:
        response = requests.post(scrappey, headers=headers, json=options)
        return response.json()
    except(ValueError, json.decoder.JSONDecodeError):
        print("Error")
        print(response)
        return None
    
async def get_data_with_proxy(data, proxy):
    data['proxy'] = proxy
    options = data
    try:
        response = requests.post(scrappey, headers=headers, json=options)
        return response.json()
    except(ValueError, json.decoder.JSONDecodeError):
        print("Error")
        print(response)
        return None
    
def get_data_with_scraping_ant():
    result = client.general_request('https://sportsbook-nash.draftkings.com/sites/US-SB/api/v4/featured/displaygroups/6/live?format=json', proxy_country='US', browser=False)
    
    
#------- General
async def scrape(data, site, attempt_count):
    logger.info(f"Scraping from {site}")

    tries = 0
    while tries < attempt_count:
        try:
            if site in proxy_needed:
                proxy = await get_proxy()
                print(f"Using proxy: {proxy}")
                response = await get_data_with_proxy(data=data, proxy=proxy)
            else:
                response = await get_data(data=data)
            if response == None:
                tries += 1
                logger.warning(f"Error getting data - Trying again - ({tries}/{attempt_count})")
            else:
                is_valid = verifier(response)
                if is_valid:
                    return response['solution']['response']
                else:
                    tries += 1
                    logger.warning(f"Error verifying data - Trying again - ({tries}/{attempt_count})")

            time.sleep(1)
        except Exception as e:
            logger.warning(f"""Error scraping live data {e}""")
            tries += 1

async def get_proxy():
    with open('flagged.txt', 'r') as f:
        flagged_proxies = f.read().splitlines()

    while True:
        proxy = FreeProxy(country_id=['US', 'CA', 'GB', 'AT', 'IE', 'MT']).get()
        if proxy not in flagged_proxies:
            return proxy
