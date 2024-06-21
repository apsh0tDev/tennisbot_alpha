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


#------- Bot Classes ------
class MarketsDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Match Winner")
        ] 

        super().__init__(placeholder="Choose a market", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        market = self.values[0]
        match market:
            case "Match Winner":
                response = await market_commands.get_match_winner()
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

@bot.event
async def on_command_error(ctx: commands.Context, error):
    try:
            # Log all unhandled errors
            logger.error(f'Ignoring exception in command {ctx.command}: {type(error).__name__}: {error}')
            await ctx.send("An error occurred. Please try again later.")
    except Exception as e:
        # Catch any exception that occurs within the error handler itself
        logger.error(f'Exception in error handler: {type(e).__name__}: {e}')

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