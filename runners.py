import time
import asyncio
import datetime as dt
from schedule import scrape_events, schedule_clean_up
from scheduler import Scheduler

schedule = Scheduler()

def run_schedule():
    asyncio.run(scrape_events())

schedule.cyclic(dt.timedelta(hours=1), run_schedule)

while True:
    schedule.exec_jobs()
    time.sleep(1)