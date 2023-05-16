import requests

# Edit config.ini when running for the first time
import sys, os
import configparser
from time import sleep
import logging 

# Custom imports
from classes.Util import WhatTheFuckDidYouDo
from classes.UI import UI
from classes.PeriodicScraper import PeriodicScraper
from classes.Scraper import Scraper

# Config section
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Check if bundled
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
elif __file__:
    base_dir = os.path.dirname(__file__)

logging.info(base_dir)
config = configparser.ConfigParser()
conf_path = os.path.join(base_dir, "config.ini")
logging.info(conf_path)
config.read(conf_path)
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
    # Running the UI
    periodic = PeriodicScraper(config=config)
    ui = UI(scraper=periodic.connector, periodic=periodic, base_dir=base_dir)
    periodic.start()
    periodic.join()
    

if __name__ == "__main__":
    main()