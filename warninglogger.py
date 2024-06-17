import os
import requests
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook

load_dotenv()

url = os.getenv("DISCORD_WEBHOOK")
webhook = DiscordWebhook(url=url, content="Today's log file:")
file_path = "./error_warnings.log"


def get_log_file():
    with open(file_path, "rb") as file:
        webhook.add_file(file=file.read(), filename="error_warnings.log")
    webhook.execute()

if __name__ == "__main__":
    get_log_file()


