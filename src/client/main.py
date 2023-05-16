import requests

# Edit config.ini when running for the first time
import sys
import configparser
from time import sleep
import logging 

# Custom imports
from classes.Util import WhatTheFuckDidYouDo
from classes.UI import UI
from classes.PeriodicScraper import PeriodicScraper
from classes.Scraper import Scraper

# Config section
config = configparser.ConfigParser()
config.read("../config.ini")
URL = config["DEFAULT"]["URL"] 
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

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
    # Running the UI
    periodic = PeriodicScraper()
    ui = UI(scraper=periodic.connector, periodic=periodic)
    periodic.start()
    periodic.join()
    

if __name__ == "__main__":
    main()