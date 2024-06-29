import time
import random
import asyncio
import datetime as dt
import draftkings
import fanduel
from loguru import logger
from schedule import scrape_events
from scheduler import Scheduler
from warninglogger import get_log_file
from live import scrape_live_events
from arb import get_moneyline


schedule = Scheduler()
logger.add("error_warnings.log", level="WARNING")
logger.add("history.log", level="INFO")

def run_live():
    asyncio.run(scrape_live_events())

def run_spiders():
    asyncio.run(fanduel.scrape_data())
    asyncio.run(draftkings.scrape_data())

def run_arb():
    asyncio.run(get_moneyline())

def run_schedule():
    asyncio.run(scrape_events())

tz_venezuela = dt.timezone(dt.timedelta(hours=-4))

schedule.cyclic(dt.timedelta(seconds=random.randrange(20, 45)), run_spiders)
schedule.cyclic(dt.timedelta(seconds=10), run_arb)
#schedule.cyclic(dt.timedelta(seconds=random.randrange(45, 60)), run_live)
#schedule.cyclic(dt.timedelta(hours=1), run_schedule)
#schedule.daily(dt.time(hour=16, minute=30), get_log_file)


while True:
    schedule.exec_jobs()
    time.sleep(1)