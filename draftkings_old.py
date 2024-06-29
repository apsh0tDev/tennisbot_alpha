import json
import asyncio
import constants
from db import db
from rich import print
from thefuzz import fuzz
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
                        markets = []
                        event_groups = []
                        for item in subcats:
                                markets.append({
                                        "subcategoryName" : item['subcategoryName'],
                                        "subcategoryId" : item['subcategoryId']
                                })

                        for item in subcats[0]['featuredEventGroupSubcategories']:
                                event_groups.append({
                                        "eventGroupId" : item['eventGroupId'],
                                        "eventGroupName" : item['eventGroupName']
                                })
                        print(markets)
                        await get_moneyline(event_groups)
                        #await get_correct_score_1(event_groups)

        except Exception as e:
                logger.warning(f"There was an Error while parsing Draftkings: {e}")

#------ Moneyline
async def get_moneyline(data):
        moneyline_table = db.table("moneyline").select("match_id").execute()
        ids = [item['match_id'] for item in moneyline_table.data]

        for item in data:
                id = item['eventGroupId']
                options = {
                        'cmd' : 'request.get',
                        'url' : f"https://sportsbook-nash.draftkings.com/sites/US-SB/api/v5/eventgroups/{id}?format=json",
                        'requestType' : 'request'
                }
                print(f"Getting info for: {item['eventGroupName']}")
                response = await scrape(options, "Draftkings", 3)
                res_load = json.loads(response)
                cleaned_data = await clean_moneyline(res_load)

                for x in cleaned_data:
                        if x['id'] not in ids:
                                info = {
                                        "match_id": x['id'],
                                        "match_name": x['match_name'],
                                        "tournament": x['tournament'],
                                        "source" : "Draftkings",
                                        "teamA" : x['outcomes']['teamA'],
                                        "teamB" : x['outcomes']['teamB']
                                }
                                await upload(info, 'moneyline')
                        else:
                                info = {
                                        "teamA" : x['outcomes']['teamA'],
                                        "teamB" : x['outcomes']['teamB']
                                }
                                await update(info, 'moneyline', x['id'])
                
async def clean_moneyline(data):
        #init events
        events_group = []
        outcomes = []
        #First get events information into array
        if 'eventGroup' in data and 'events' in data['eventGroup']:
                events = data['eventGroup']['events']
                for event in events:
                        events_group.append({
                                "id" : event['eventId'],
                                "tournament" : event['eventGroupName'],
                                "match_name" : event['name'],
                                "teamA": event['team1']['name'],
                                "teamB": event['team2']['name']  
                        })

        #Then get the offers
        if 'eventGroup' in data and 'offerCategories' in data['eventGroup']:
                short = data['eventGroup']['offerCategories'][0]['offerSubcategoryDescriptors']     
                if 'offerSubcategory' in short[0] and 'offers' in short[0]['offerSubcategory']:
                        offers = short[0]['offerSubcategory']['offers']
                        for offer in offers:
                                outcomes.append({
                                        "eventId" : offer[0]['eventId'],
                                        "outcomes" : {
                                                "teamA" : {
                                                        "name" : offer[0]['outcomes'][0]['label'],
                                                        "oddsAmerican" : offer[0]['outcomes'][0]['oddsAmerican'],
                                                        "oddsDecimal" : offer[0]['outcomes'][0]['oddsDecimal']
                                                },
                                                "teamB" : {
                                                        "name" : offer[0]['outcomes'][1]['label'],
                                                        "oddsAmerican" : offer[0]['outcomes'][1]['oddsAmerican'],
                                                        "oddsDecimal" : offer[0]['outcomes'][1]['oddsDecimal']
                                                }
                                        }
                                })

        #Merge both groups
        event_outcomes = {item["eventId"]: item["outcomes"] for item in outcomes}
        for item in events_group:
                if item['id'] in event_outcomes:
                        item["outcomes"] = event_outcomes[item["id"]]
        
        return events_group

#------ End of Moneyline

#------ Correct Score - 1st Set
async def get_correct_score_1(data):
        subcategoryId = "5904"
        for group in data:
                groupId = group['eventGroupId']
                options = {
                        'cmd' : 'request.get',
                        'url' : f"https://sportsbook-nash-usva.draftkings.com/sites/US-VA-SB/api/v4/featured/displaygroups/6/subcategory/{subcategoryId}/eventgroup/{groupId}/live?format=json",
                        'requestType' : 'request'
                }
                print(f"Getting correct score info for: {group['eventGroupName']}")
                response = await scrape(options, "Draftkings", 3)
                res_load = json.loads(response)
                cleaned_data = await clean_correct_score_1(res_load)
                print(cleaned_data)

async def clean_correct_score_1(data):
        subcategoryId = 5904
        if 'featuredDisplayGroup' in data and 'featuredSubcategories' in data['featuredDisplayGroup']:
                arr = data['featuredDisplayGroup']['featuredSubcategories']
                for cat in arr:
                        if 'featuredEventGroupSubcategories' in cat and cat['subcategoryId'] == subcategoryId:
                                res = cat['featuredEventGroupSubcategories'][0]
                                tournament = res['eventGroupName']
                                if 'offers' in res:
                                        offers = res['offers']
                                        for offer in offers:
                                                info = {
                                                        "match_id" : offer[0]['eventId'],
                                                        "tournament" : tournament,
                                                }

                                                participants = []
                                                outcomes = []
                                                for outcome in offer[0]['outcomes']:
                                                       participants.append(outcome['participant'])
                                                       if 'label' in outcome and 'participant' in outcome and 'oddsAmerican' in outcome and 'oddsDecimal' in outcome:
                                                               outcomes.append({
                                                                       "label" : outcome["label"],
                                                                       "participant": outcome["participant"],
                                                                       "oddsAmerican" : outcome["oddsAmerican"],
                                                                       "oddsDecimal" : outcome["oddsDecimal"],
                                                               })
                                                participants = list(set(participants))
                                                info['teamA'] = participants[0]
                                                info['teamB'] = participants[1]
                                                info['outcomes'] = outcomes
                                        
                                else:
                                        print("This event doesn't have live 'Correct score - 1st Set' offers.")
                                        








#------ Correct Score - 2nd Set
                
async def update(data, table, id):
        print(data, id)
        response = db.table(table).update(data).eq('id', id).execute()
        print(response)

async def upload(data, table):
        response = db.table(table).insert(data).execute()
        print(response)
      

if __name__ == "__main__":
        asyncio.run(scrape_data())