
import json
import discord
import asyncio
import constants
from db import db
from rich import print
from utils import verifier, remove_parentheses, format_datetime
from loguru import logger
from connection import get_data


async def scrape_events():
    logger.info("Scraping Schedule events from BetMGM")
    #No need for proxy
    data = {
        'cmd' : 'request.get',
        'url' : constants.schedule_url,
        'requestType' : 'request'
    }
    attempt_count = 1
    while attempt_count < 3:
        try:
            response = await get_data(data=data)
            if response == None:
                logger.warning(f"Error getting BetMGM Data - Trying again")
                attempt_count += 1
            else:
                #Verifier function
                is_valid = verifier(response) #TODO verifier
                if is_valid:
                    await scheduler_parser(response=response)
                    break
                else:
                    logger.warning(f"Error verifying schedule")

        except Exception as e:
            attempt_count += 1
            logger.warning(f"""Error scraping schedule
                            {e}""")
            
        
async def scheduler_parser(response):
    schedule_table = db.table("schedule").select("match_id").execute()
    matches_ids = [item['match_id'] for item in schedule_table.data]
    # Collects the previous schedule data, and saves the ids of the matches
    # later we need to compared them to the new fetched data, to avoid posting duplicate matches

    try:
        load = json.loads(response['solution']['response'])
        if 'widgets' in load and 'payload' in load['widgets'][0] and 'fixtures' in load['widgets'][0]['payload']:
            fixtures = load['widgets'][0]['payload']['fixtures']
            
            for match in fixtures:
                teamA = f"{remove_parentheses(match['participants'][0]['name']['value']) if len(match['participants']) > 0 else "Unknown"}"
                teamB = f"{remove_parentheses(match['participants'][1]['name']['value']) if len(match['participants']) > 1 else "Unknown"}"

                match_info = {
                    "match_id" : match['id'],
                    "match_name" : match['name']['value'],
                    "tournament" : match['tournament']['name']['value'],
                    "tournament_display_name": match['competition']['name']['value'],
                    "date" : match['startDate'],
                    "teamA" : teamA.strip(),
                    "teamB" : teamB.strip(),
                    "status" : match['stage']
                }    
                #Post it to the database
                if match['id'] not in matches_ids:
                    try:
                        response = db.table("schedule").insert(match_info).execute()
                    except Exception as e:
                        logger.error(f"There was an Error while uploading to the database: {e}")
                elif match['id'] in matches_ids and match['stage'] == "Live":
                    logger.info(f"Match {match['id']} already started!")
                    await schedule_clean_up(match['id'])
                else:
                    logger.info(f"Match {match['id']} already exists in table. Skipping.")

    except Exception as e:
        logger.warning(f"There was an Error while parsing the schedule: {e}")

# This function retrieves the schedule data from the database
# Conditional "toDiscord" to use the formatter into text and return it, oderwise, returns a JSON

async def get_schedule(toDiscord: bool):
    result = db.table("schedule").select("*").execute()
    response = "Oops, something wrong happened while retrieving the schedule, please try again later"
    
    #TODO handle supabase errors
    if toDiscord:
        response = await format_schedule(result.data)
    return response

#Formats the schedule data and returns a discord-friendly message
async def format_schedule(data):
    logger.info("Formatting schedule for discord")
    if len(data) > 0:
        try:
            fields_added = 0
            embeds = []
            current_embed = discord.Embed(title="Schedule 📅")

            for event in data:
                event_name = event.get('match_name', '')
                event_tournament = event.get('tournament', '')
                event_date = format_datetime(event.get('date', ''))
                if isinstance(event_name, str) and event_name.strip() != '' and isinstance(event_tournament, str) and event_tournament.strip() != '' and isinstance(event_date, str) and event_date.strip() != '':
                    field_value = f"{event_tournament} - {event_date}"
                    if len(current_embed) + len(event_name) + len(field_value) <= 6000 and fields_added < 25:
                            current_embed.add_field(name=event_name, value=field_value, inline=False)
                            fields_added += 1
                    else:
                            embeds.append(current_embed)
                            current_embed = discord.Embed(title="Schedule 📅")
                            fields_added = 0

            embeds.append(current_embed)
            for index, embed in enumerate(embeds):
                if index < 10:  # Limit to 10 embeds per message
                    return embed
                else:
                    logger.warning("Maximum number of embeds per message reached")
                    break 
        except Exception as e:
            logger.error(f"There was an Error formatting the message: {e}")
    else:
        return "No events scheduled."
    

#--- Clean up function - use carefully
async def schedule_clean_up(id):
    logger.info("Running clean up 🧹")
    db.table("schedule").delete().eq('id', id).execute()
    logger.info("Cleanup Done!")


if __name__ == "__main__":
    asyncio.run(scrape_events())
