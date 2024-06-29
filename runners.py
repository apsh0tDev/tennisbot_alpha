import time
import random
import asyncio
import datetime as dt
import draftkings
import fanduel
from loguru import logger
from arb import get_moneyline
from live import scrape_live_events
from schedule import scrape_events, get_start_hour
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
logger.add("error_warnings.log", level="WARNING")
logger.add("history.log", level="INFO")

def scrape_fanduel():
    asyncio.run(fanduel.scrape_data())

def scrape_draftkings():
    asyncio.run(draftkings.scrape_data())

def get_live_data():
    asyncio.run(scrape_live_events())

def get_schedule():
    iso_datetime = get_start_hour()
    dt_object = dt.datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))

    now = dt.datetime.now(dt.timezone.utc)
    time_difference = dt_object - now
    if 0 < time_difference.total_seconds() < 3600:
        print("The event starts within an hour.")
        
        jobs = scheduler.get_jobs()
        jobs_names = []
        for job in jobs:
            jobs_names.append(job.name)

        if 'get_live_data' not in jobs_names:
            scheduler.add_job(get_live_data, 'interval', minutes=1)

        if 'scrape_fan_duel' not in jobs_names:
            scheduler.add_job(scrape_fanduel, 'interval', seconds=40)
        
        if 'scrape_draftkings' not in jobs_names:
            scheduler.add_job(scrape_draftkings, 'interval', seconds=45)
    else:
        print("The event does not start within an hour.")
    
    asyncio.run(scrape_events())


job_defaults = {
    'coalesce': False,
    'max_instances': 10
}
scheduler.configure(job_defaults=job_defaults)
scheduler.add_job(get_schedule, 'interval', seconds=10)


scheduler.start()

def print_current_jobs():
    jobs = scheduler.get_jobs()
    for job in jobs:
        print(f"{job}")

print_current_jobs()

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
