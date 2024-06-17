import os
import json
import requests
from rich import print
from typing import Literal
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("SCRAPPEY_KEY")
provider: Literal["Scrappey", "AnyIP"] = "AnyIP"

headers = { 'Content-Type' : 'application/json' }
scrappey = f"https://publisher.scrappey.com/api/v1?key={key}"

#TODO add banned validation
async def get_data(data):
    options = data
    try:
        response = requests.post(scrappey, headers=headers, json=options)
        return response.json()
    except(ValueError, json.decoder.JSONDecodeError):
        print("Error")
        print(response)
        return None