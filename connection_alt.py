import os
import json
import asyncio
import requests
from rich import print
from loguru import logger
from dotenv import load_dotenv
from scrapingant_client import ScrapingAntClient

load_dotenv()
key = os.getenv("SCRAPING_ANT_TOKEN")
client = ScrapingAntClient(token=key)

async def get_data():
    try:
        result = client.general_request(f"https://sbapi.ny.sportsbook.fanduel.com/api/content-managed-page?page=SPORT&eventTypeId=2&_ak=FhMFpcPWXMeyZxOx&timezone=America%2FNew_York", proxy_country='US', browser=False)
        print(result.status_code)
        load = json.loads(result.content)
        print(load)

    except Exception as e:
        logger.info(e)

if __name__ == "__main__":
    asyncio.run(get_data())