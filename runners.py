import time
import asyncio
import datetime as dt
from loguru import logger
from schedule import scrape_events
from scheduler import Scheduler

schedule = Scheduler()
logger.add("error_warnings.log", level="WARNING")

def run_schedule():
    asyncio.run(scrape_events())

schedule.cyclic(dt.timedelta(hours=1), run_schedule)

while True:
    schedule.exec_jobs()
    time.sleep(1)