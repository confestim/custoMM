import pystray
from PIL import Image
import pyautogui
from time import sleep
import os
from logging import info
from .Scraper import Scraper
from .PeriodicScraper import PeriodicScraper
from .SelfUpdate import SelfUpdate

VERSION = "1.1.1"

class UI():
    """Tray icon UI module

        Args:
            scraper (Scraper): Scraper instance
            periodic (PeriodicScraper): PeriodicScraper instance
            base_dir (_type_): Base dir of program
    """
    def __init__(self,scraper:Scraper, periodic:PeriodicScraper, base_dir):
        
        self.version = VERSION
        image = Image.open(os.path.join(base_dir, os.path.join("assets", "icon.png")))
        self.base_dir = base_dir
        # Check if user has exited before making a connection with the LoL client
        if periodic.closed:
            return
        self.periodic = periodic
        self.scraper = scraper

        # Menu items
        self.menu = pystray.Menu(
            pystray.MenuItem(
                "Check registration", self.check_registration, default=True
            ),
            pystray.MenuItem(
                f"Manual game report", self.report
            ),
            pystray.MenuItem(
                f"Check for game", self.check
            ),
            pystray.MenuItem(
                "Check for updates", self.update_check
            ),
            pystray.MenuItem(
                "Exit", self.quit
            )
        )

        self.icon = pystray.Icon(
            "name", image, "custoMM", self.menu)
        self.icon.run_detached()
        
        # After ui is running, check user registration
        self.check_registration()
        self.update_check()
        
    def update_check(self):
        # TODO: Test this
        update = SelfUpdate(base_dir=self.base_dir, version=self.version)
        if update:
            prompt = pyautogui.confirm(f"New version available, do you want to update?")
            if prompt:
                update.update()
            else:
                self.icon.notify("Please update as soon as possible.", "New version available.")
    
    def check(self):
        """ Checks for ongoing game and notifies user
        """

        self.icon.notify("This is discouraged, as it is done automatically.", "Checking for game...")
        game = self.scraper.check_for_game()
        if game == "NO_GAME":
            self.icon.notify("Please create a game on discord.", "No game found.")
        elif game == "CREATED":
            self.icon.notify("GLHF!", "You are the host of a new game!")
        elif game == "JOINED":
            self.icon.notify("Waiting for players...", "Game joined!")

    def report(self):
        """ Manual game reporting
        """
        self.icon.notify("Game report initiated.")
        self.scraper.scrape()
            

    def check_registration(self):
        """ Checks the current logged in user's registration
        """
        self.icon.notify("Checking summoner...", title="custoMM")
        
        check = self.scraper.check_summoner()
        if check == "UNCLAIMED" or check == "USER_DOES_NOT_EXIST":
            self.icon.notify("You have not claimed your account yet, please claim it on discord -> !register <ACCOUNT_NAME>.")

        elif check[0] == "REGISTRATION_IN_PROGRESS":
            prompt = pyautogui.confirm(f"Your account({check[1]['lol']}) is currently being registered by {check[1]['discord']} on Discord. Is this you?")
            if prompt:
                self.scraper.register_summoner(True, check[1])
            else:
                self.scraper.register_summoner(False, check[1])
        else:
            self.icon.notify(f"Your account is registered to {check[0]} and your account name is {check[1]}.")
    
    
    def quit(self, icon):
        """ Quit
        """
        icon.stop()
        self.periodic.closed = True

