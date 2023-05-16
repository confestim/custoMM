from time import sleep
from threading import Thread
from .Scraper import Scraper
import logging

class PeriodicScraper(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.daemon = True
        self.connector:Scraper = Scraper(config=config)
        self.closed = False

    def run(self):
        while True:
            if self.closed:
                self.connector.connection.stop()
                break
        
            game_state = self.connector.check_for_game()
            
            logging.info("Scraping...")
            self.connector.scrape()
            sleep(5)