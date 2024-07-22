import re
import pytz
from datetime import datetime, timezone
from loguru import logger
import datetime as dt

def verifier(value):
    if 'solution' in value and 'verified' in value['solution'] and value['solution']['verified'] == True:
        return True
    else:
        logger.error(value)
        return False
    
def remove_parentheses(text):
    return re.sub(r'\([^)]*\)', '', text)

def format_match_name(text):
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\s*-\s*', ' vs ', text)
    return text.strip()

def format_datetime(input_datetime_str):
    input_datetime = datetime.fromisoformat(input_datetime_str.replace('Z', '+00:00'))
    ny_timezone = pytz.timezone('America/New_York')
    input_datetime = input_datetime.astimezone(ny_timezone)
    current_datetime = datetime.now(ny_timezone)
    day_difference = (input_datetime.date() - current_datetime.date()).days
    if day_difference == 0:
        day_str = "Today"
    elif day_difference == 1:
        day_str = "Tomorrow"
    else:
        day_str = input_datetime.strftime("%A")
    time_str = input_datetime.strftime("%I:%M %p")

    return f"{day_str} - {time_str}"

def remove_year(text):
    # This regex looks for a four-digit number (representing a year) and removes it
    return re.sub(r'\b\d{4}\b', '', text).strip()

def remove_after_comma(s):
    return s.split(',')[0]

from datetime import datetime, timezone

def time_ago(datetime_str):
   
    input_time = datetime.fromisoformat(datetime_str)
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - input_time
    seconds = time_diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    if days >= 1:
        return f"{int(days)} days ago"
    elif hours >= 1:
        return f"{int(hours)} hours ago"
    elif minutes >= 1:
        return f"{int(minutes)} minutes ago"
    else:
        return f"{int(seconds)} seconds ago"
    
def extract_players(matchup):
    return matchup.split(" v ")

def separate_name_and_score(player_score):
    match = re.match(r"^(.*?)(\d+-\d+)$", player_score)
    if match:
        name = match.group(1).strip()
        score = match.group(2).strip()
        return name, score
    else:
        return None, None
    
def extract_set_and_games(description):
    match = re.search(r'Set (\d+) Race to (\d+) Games', description)
    if match:
        set_number = int(match.group(1))
        game_number = int(match.group(2))
        return set_number, game_number
    return None, None




#------- ONLY FOR TESTING

def get_start_hour_for_testing():
    # Get the current time in UTC
    now = dt.datetime.now(dt.timezone.utc)
    # Set the event start time to 45 minutes from now
    event_start_time = now + dt.timedelta(minutes=45)
    # Convert the event start time to ISO format
    event_start_iso = event_start_time.isoformat().replace("+00:00", "Z")
    file = open("start_at.dat", "w")
    file.write(event_start_iso)


if __name__ == "__main__":
    get_start_hour_for_testing()
