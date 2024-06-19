import time
import random
import asyncio
import datetime as dt
from loguru import logger
from schedule import scrape_events
from scheduler import Scheduler
from warninglogger import get_log_file
from live import scrape_live_events

schedule = Scheduler()
logger.add("error_warnings.log", level="WARNING")
interval = random.randrange(30, 60)

def run_live():
    asyncio.run(scrape_live_events())

def run_schedule():
    asyncio.run(scrape_events())

tz_venezuela = dt.timezone(dt.timedelta(hours=-4))

schedule.cyclic(dt.timedelta(hours=1), run_schedule)
schedule.daily(dt.time(hour=16, minute=30), get_log_file)
#schedule.cyclic(dt.timedelta(seconds=interval), run_live)

while True:
    schedule.exec_jobs()
    time.sleep(1)