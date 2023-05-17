import requests

# Edit config.ini when running for the first time
import sys, os
import configparser
from time import sleep
from logging import info, basicConfig, INFO

# Custom imports
from classes.Util import WhatTheFuckDidYouDo
from classes.UI import UI
from classes.PeriodicScraper import PeriodicScraper
from classes.Scraper import Scraper
from classes.SelfUpdate import SelfUpdate
from classes.Notify import Notify

VERSION = "1.1.1"

# Config section
basicConfig(format='%(asctime)s - %(message)s', level=INFO)

# Check if bundled
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
elif __file__:
    base_dir = os.path.dirname(__file__)

info("Base directory - " + base_dir)

# Parse config
config = configparser.ConfigParser()
conf_path = os.path.join(base_dir, "config.ini")
config.read(conf_path)
URL = config["DEFAULT"]["URL"] 


# Test connection to server
try:
    test = requests.get(URL).json()

except Exception:
    # NEVER DO THIS
    # although, what could go wrong...
    Notify(base_dir=base_dir, exit_after=True).notification("Server seems to be down, please contact admin if it keeps doing this")
    sys.exit()

# Get current summoner
def main():
    # Match scraping
    # Periodic scraper
    periodic = PeriodicScraper(config=config, base_dir=base_dir)
    
    ui = UI(scraper=periodic.connector, periodic=periodic, base_dir=base_dir)
    # Self update only needs to run once, on start of program
    # TODO: Test this
    update = SelfUpdate(base_dir=base_dir, version=VERSION)
    periodic.start()
    periodic.join()
    

if __name__ == "__main__":
    main()