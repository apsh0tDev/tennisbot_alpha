import time
import random
import asyncio
import datetime as dt
import draftkings
import fanduel
import betmgm
from loguru import logger
from arb_old import get_moneyline
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

def scrape_betmgm():
    asyncio.run(betmgm.scrape_data())    

def get_live_data():
    asyncio.run(scrape_live_events())

def arbitrage():
    asyncio.run(get_moneyline())

def get_schedule():
    iso_datetime = get_start_hour()
    dt_object = dt.datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))

    now = dt.datetime.now(dt.timezone.utc)
    time_difference = dt_object - now
    if 0 < time_difference.total_seconds() < 3600:
        print("The event starts within an hour.")
    else:
        print("The event does not start within an hour.")
    
    asyncio.run(scrape_events())

def get_live():
    jobs = scheduler.get_jobs()
    jobs_names = []
    for job in jobs:
        jobs_names.append(job.name)

    """if 'get_live_data' not in jobs_names:
        scheduler.add_job(get_live_data, 'interval', minutes=1)"""

    """if 'scrape_fan_duel' not in jobs_names:
        scheduler.add_job(scrape_fanduel, 'interval', seconds=40)"""
    
    if 'scrape_betmgm' not in jobs_names:
        scheduler.add_job(scrape_betmgm, 'interval', seconds=15)
    
    """if 'scrape_draftkings' not in jobs_names:
        scheduler.add_job(scrape_draftkings, 'interval', seconds=45)"""

job_defaults = {
    'coalesce': False,
    'max_instances': 10
}
scheduler.configure(job_defaults=job_defaults)
scheduler.add_job(get_live, 'interval', minutes=1)
scheduler.add_job(get_schedule, 'interval', minutes=30)


scheduler.start()

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
