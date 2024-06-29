import os
import traceback
import discord
import textwrap
import constants
import market_commands
from loguru import logger
from live import get_live_matches
from schedule import get_schedule
from dotenv import load_dotenv
from discord.ext import commands, tasks



#---Init
load_dotenv()

current_branch = "PROD"
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


#------- Bot Classes ------
class MarketsDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moneyline")
            #discord.SelectOption(label="Match Winner"),
            #discord.SelectOption(label="Set 1 Winner")
        ] 

        super().__init__(placeholder="Choose a market", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        market = self.values[0]
        standard = ["Match Winner", "Set 1 Winner"]
        if market in standard:
            match market:
                case "Match Winner":
                    table = "match_winner"
                case "Set 1 Winner":
                    table = "set_one_winner"
                    
            response = await market_commands.get_standard_data(table=table)
            if response:
                    await interaction.response.send_message(f"```{response[0]}```")
                    for item in response[1:]:
                        await interaction.followup.send(f"```{item}```")
            else:
                await interaction.response.send_message("No data to display.")

class MarketsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MarketsDropdown())

#------- Bot Events -------
@bot.event
async def on_ready():
    print("Bot running")
    status_checker.start()

@bot.event
async def on_command_error(ctx: commands.Context, error):
    try:
            # Log all unhandled errors
            logger.error(f'Ignoring exception in command {ctx.command}: {type(error).__name__}: {error}')
            await ctx.send("An error occurred. Please try again later.")
    except Exception as e:
        # Catch any exception that occurs within the error handler itself
        logger.error(f'Exception in error handler: {type(e).__name__}: {e}')

#------- Bot Tasks -------
@tasks.loop(hours=1)
async def status_checker():
        print("Checking status...")
        file = open("runner_status.dat", "r")
        status = str(file.read())
        if status == "Live":
            await bot.change_presence(status=discord.Status.online)
        elif status == "Not_Live":
            await bot.change_presence(status=discord.Status.idle)

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
    response = await get_live_matches()
    if response != None:
        message = textwrap.dedent(response)
        await ctx.send(message)
    else:
        await ctx.send("No live matches are on at the moment.")

@bot.command()
async def markets(ctx):
    await ctx.send("Click on the dropdown below to choose the markert", view=MarketsView())

if __name__ == "__main__":
    bot.run(get_token())
