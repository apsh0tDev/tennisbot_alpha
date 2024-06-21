import os
import json
import requests
from rich import print
from loguru import logger
from utils import verifier
from typing import Literal
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("SCRAPPEY_KEY")
provider: Literal["Scrappey", "AnyIP"] = "AnyIP"

headers = { 'Content-Type' : 'application/json' }
scrappey = f"https://publisher.scrappey.com/api/v1?key={key}"

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
    

#------- General
async def scrape(data, site, attempt_count):
    logger.info(f"Scraping from {site}")

    tries = 0
    while tries < attempt_count:
        try:
            response = await get_data(data=data)
            if response == None:
                logger.warning(f"Error getting data - Trying again - ({tries}/{attempt_count})")
                tries += 1
            else:
                is_valid = verifier(response)
                if is_valid:
                    return response['solution']['response']
                else:
                    logger.warning(f"Error verifying data - Trying gaian - ({tries}/{attempt_count})")
                    tries += 1
        except Exception as e:
            logger.warning(f"""Error scraping live data {e}""")
            tries += 1