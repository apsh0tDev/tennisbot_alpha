import os
import discord
import constants
from schedule import get_schedule
from dotenv import load_dotenv
from discord.ext import commands


#---Init
load_dotenv()

current_branch = "DEV"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

#Dynamic token fetcher
def get_token():
    DISCORD_API = ''
    if current_branch == "DEV":
        DISCORD_API = os.getenv("TOKEN_DEV")
    elif current_branch == "PROD":
        DISCORD_API = os.getenv("TOKEN_PROD")
    return DISCORD_API

#------- Bot Events -------
@bot.event
async def on_ready():
    print("Bot running")

#------- Bot Commands ------
@bot.command()
async def commands(ctx):
    message = constants.commands_message
    await ctx.send(message)

@bot.command()
async def schedule(ctx):
    # Uses the get_schedule function caller.py
    # This gets all events from "matches" table that have a PreMatch status.
    # This table fills with BetMGM Data  
    message = await get_schedule(toDiscord=True)
    #Check if the message is a string or an embed an send the message type accordingly
    if isinstance(message, str):
        await ctx.send(message)
    else:
        await ctx.send(embed=message)

@bot.command()
async def live(ctx):
    await ctx.send("Getting live matches...")

@bot.command()
async def sportsbooks(ctx):
    await ctx.send("Available sportsbooks...")

@bot.command()
async def markets(ctx):
    await ctx.send("Markets...")

if __name__ == "__main__":
    bot.run(get_token())