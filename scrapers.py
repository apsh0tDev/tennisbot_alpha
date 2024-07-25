import betmgm
import fanduel
import draftkings
import asyncio

async def scrape_all():
    tasks = [betmgm.scrape_data(), fanduel.scrape_data()]
    await asyncio.gather(*tasks)
    await draftkings.scrape_data()

if __name__ == "__main__":
    asyncio.run(scrape_all())