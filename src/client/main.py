import requests

# Edit config.ini when running for the first time
import sys
import configparser
from time import sleep
import threading 

# Custom imports
from classes.Util import WhatTheFuckDidYouDo
from classes.UI import UI
from classes.PeriodicScraper import PeriodicScraper
from classes.Scraper import Scraper

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

# Get current summoner
def main():
    # Match scraping
    scraper = Scraper()
    periodic = PeriodicScraper()
    # Running the UI
    ui = UI(scraper=scraper)
    
    # Loop until close, let stuff kill itself
    while threading.active_count() >= 3:
        sleep(10)
if __name__ == "__main__":
    main()