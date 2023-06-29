import requests

# Edit config.ini when running for the first time
import sys, os
import configparser
from time import sleep
from logging import info, basicConfig, INFO

# Custom imports
from classes.UI import UI
from classes.PeriodicScraper import PeriodicScraper
from classes.Scraper import Scraper
from classes.SelfUpdate import SelfUpdate
from classes.Notify import Notify

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

Notify(base_dir=base_dir, exit_after=True).notification("Starting custoMM...")

# Test connection to server
try:
    test = requests.get(URL).raise_for_status()

except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
    # NEVER DO THIS
    # although, what could go wrong...
    Notify(base_dir=base_dir, exit_after=True).notification("custoMM unavailable", "Try restarting and contact admin if it keeps doing this.")
    sys.exit()
except requests.exceptions.HTTPError as error:
    Notify(base_dir=base_dir, exit_after=True).notification(f"Server issue", "Contact admin immediately. Error code: {error.response.status_code}")
    sys.exit()

# Get current summoner
def main():
    # Match scraping
    # Periodic scraper
    periodic = PeriodicScraper(config=config, base_dir=base_dir, offset=30)
    
    ui = UI(scraper=periodic.connector, periodic=periodic, base_dir=base_dir)
    # Self update only needs to run once, on start of program
    periodic.start()
    periodic.join()
    

if __name__ == "__main__":
    main()