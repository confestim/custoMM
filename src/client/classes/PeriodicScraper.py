from time import sleep
from threading import Thread
from .Scraper import Scraper
from logging import info
from sys import exit
from configparser import ConfigParser


class PeriodicScraper(Thread):
    """Scraper that runs every `offset` seconds

        Args:
            config (ConfigParser): Config instance
            base_dir (_type_): Base dir of program
            offset (int, optional): Seconds to sleep before repeat. Defaults to 5.
    """

    def __init__(self, config:ConfigParser, base_dir, offset:int=5):
       
         
        Thread.__init__(self)
        self.offset=offset
        self.daemon = True
        self.connector:Scraper = Scraper(config=config, base_dir=base_dir)
        self.closed = not self.connector.conn

    def run(self):
        
        while True:
            if self.closed:
                try:
                    self.connector.connection.stop()
                except AttributeError:
                    pass
                break

            info("Checking for game...")
            game_state = self.connector.check_for_game()
            sleep(self.offset/2)
            info("Scraping...")
            self.connector.scrape()
            sleep(self.offset/22)
        return