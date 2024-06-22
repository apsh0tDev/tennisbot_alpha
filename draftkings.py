import json
import asyncio
import constants
from rich import print
from loguru import logger
from connection import scrape


async def scrape_data():
        data = {
        'cmd' : 'request.get',
        'url' : constants.draftkings_url,
        'requestType' : 'request'
        }

        response = await scrape(data, "Draftkings", 3)
        try:
                load = json.loads(response)
                if 'featuredDisplayGroup' in load and 'featuredSubcategories' in load['featuredDisplayGroup']:
                        subcats = load['featuredDisplayGroup']['featuredSubcategories']
                        grouIds = []
                        for eventGroup in subcats[0]['featuredEventGroupSubcategories']:
                                grouIds.append(eventGroup['eventGroupId'])
                        for id in grouIds:
                                data = {
                                'cmd' : 'request.get',
                                'url' : f"https://sportsbook-nash.draftkings.com/sites/US-SB/api/v5/eventgroups/{id}?format=json",
                                'requestType' : 'request'
                                }
                                response = await scrape(data, "Draftkings", 3)
                                res_load = json.loads(response)
                                await get_moneyline(res_load)
                                

        except Exception as e:
                logger.warning(f"There was an Error while parsing Draftkings: {e}")

async def get_moneyline(data):
    if 'eventGroup' in data:
           info = {}
           #Get events names
           if 'events' in data['eventGroup']:
            events = data['eventGroup']['events']
            for event in events:
                    event_name = event['name']
                    teamA = event['team1']['name'],
                    teamB = event['team2']['name']
            

            #Get events offers
            if 'offerCategories' in data['eventGroup']:
                    offerCategories = data['eventGroup']['offerCategories']
                    for cat in offerCategories:
                        if 'offerSubcategoryDescriptors' in cat and 'offerSubcategory' in cat['offerSubcategoryDescriptors'][0]:
                            offers = cat['offerSubcategoryDescriptors'][0]['offerSubcategory']['offers']
                            for offer in offers:
                                   for outcome in offer['outcomes']:
                                          print(outcome['participant'])
                                          print(outcome['oddsAmerican'])

if __name__ == "__main__":
        asyncio.run(scrape_data())