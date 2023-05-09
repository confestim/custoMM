from time import sleep
from threading import Thread
from .Scraper import Scraper

class PeriodicScraper(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.connector:Scraper = Scraper()
        self.start()

    def run(self):
        while True:
            self.connector.scrape()
            sleep(5 * 60)