from classes.LolScraper import LolScraper
import requests

# Edit config.ini when running for the first time
import sys
import configparser
from time import sleep
import threading 
# Custom imports
from classes.Util import WhatTheFuckDidYouDo
from classes.UI import UI
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

def scrape_periodically():
    sleep(5)
    while True:
        connector:LolScraper = LolScraper()
        connector.scrape()
        sleep(5 * 60)

# Get current summoner
def main():
    # Match scraping
    
    instance:UI = UI()
    
    threading.Thread(target=scrape_periodically).start()
    
if __name__ == "__main__":
    main()