import pystray
from PIL import Image
from .Scraper import Scraper
image = Image.open("assets/icon.png")
import pyautogui
from time import sleep
import logging

class UI():
	
    def __init__(self,scraper):

        self.menu = pystray.Menu(
            pystray.MenuItem(
                "Check registration", self.check_registration, default=True
            ),
            pystray.MenuItem(
                f"Manual game report", self.report_game
            ),
            pystray.MenuItem(
                "Exit", self.quit
            )
        )
        self.icon = pystray.Icon(
            "name", image, "CustoMM", self.menu)
        self.scraper = scraper
        self.check_registration()
        self.icon.run_detached()
        

    def report_game(self):
        self.icon.notify("Game report initiated.")
        logging.warning(self.icon)
        self.scraper.scrape()
        self.icon.notify("Game reported", "Your game has been reported to the server.")
            

    def check_registration(self):
        check = self.scraper.check_summoner()
        if check == "USER_DOES_NOT_EXIST":
            self.icon.notify("You are not registered, please register on the website.")
        elif check == "UNCLAIMED":
            self.icon.notify("You have not claimed your account yet, please claim it on discord -> !registed <ACCOUNT_NAME>.")
        elif check[0] == "REGISTRATION_IN_PROGRESS":
            prompt = pyautogui.confirm(f"Your account is currently being registered by {check[1]}, do you want to proceed?")
            if prompt:
                self.scraper.register_summoner(True, check[1])
            else:
                self.scraper.register_summoner(False, check[1])
        else:
            self.icon.notify(f"Your account is registered to {check[0]} and your account name is {check[1]}.")
    
    
    def quit(self, icon, query):
        icon.stop()

