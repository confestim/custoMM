from classes.LolScraper import LolScraper
import requests

# Edit config.ini when running for the first time
import asyncio
import time, sys
import configparser

# Custom imports
from classes.Util import WhatTheFuckDidYouDo

# Config section
config = configparser.ConfigParser()
config.read("../config.ini")
URL = config["DEFAULT"]["URL"] 

# Test connection to server
try:
    test = requests.get(URL).json()

except Exception:
    # NEVER DO THIS
    # although, what could go wrong...
    print("Server seems to be down, please contact admin if it keeps doing this")
    sys.exit()


# needed for windows
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Init connection
connector = LolScraper( )

# Get current summoner
@connector.ready
async def main():
    await LolScraper.scrape()