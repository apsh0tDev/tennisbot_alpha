import os
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook


current_branch = "DEV"

def get_token():
    DISCORD_API = ''
    if current_branch == "DEV":
        DISCORD_API = os.getenv("DISCORD_WEBHOOK_DEV")
    elif current_branch == "PROD":
        DISCORD_API = os.getenv("DISCORD_WEBHOOK_PROD")
    return DISCORD_API

discord = DiscordWebhook(url=get_token())

def notification(message):
    discord.content=message
    discord.execute()