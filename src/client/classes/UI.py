import pystray
from PIL import Image
from .Scraper import Scraper
import pyautogui
from time import sleep
import sys, os

class UI():
	
    def __init__(self,scraper, periodic, base_dir):
        
        image = Image.open(os.path.join(base_dir, os.path.join("assets", "icon.png")))
        
        self.periodic = periodic
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
                "Exit", self.quit
            )
        )
        self.icon = pystray.Icon(
            "name", image, "CustoMM", self.menu)
        self.scraper = scraper
        self.icon.run_detached()
        self.icon.notify("CustoMM is running in the background.", title="CustoMM")
        self.check_registration()
        
    def check(self):
        self.icon.notify("This is discouraged, as it is done automatically anyway.", "Checking for game...", title="CustoMM")
        game = self.scraper.check_for_game()
        if game == "NO_GAME":
            self.icon.notify("Please create a game on discord.", "No game found.", title="CustoMM")
        elif game == "CREATED":
            self.icon.notify("GLHF!", "You are the host of a new game!", title="CustoMM")
        elif game == "JOINED":
            self.icon.notify("Waiting for players...", "Game joined!", title="CustoMM")

    def report(self):
        self.icon.notify("Game report initiated.")
        self.scraper.scrape()
        self.icon.notify("Game reported", "Your game has been reported to the server.", title="CustoMM")
            

    def check_registration(self):
        check = self.scraper.check_summoner()
        if check == "USER_DOES_NOT_EXIST":
            self.icon.notify("You are not registered, please register on the website.", title="CustoMM")
        elif check == "UNCLAIMED":
            self.icon.notify("You have not claimed your account yet, please claim it on discord -> !registed <ACCOUNT_NAME>.", title="CustoMM")
        elif check[0] == "REGISTRATION_IN_PROGRESS":
            prompt = pyautogui.confirm(f"Your account is currently being registered by {check[1]}, do you want to proceed?")
            if prompt:
                self.scraper.register_summoner(True, check[1])
            else:
                self.scraper.register_summoner(False, check[1])
        else:
            self.icon.notify(f"Your account is registered to {check[0]} and your account name is {check[1]}.", title="CustoMM")
    
    
    def quit(self, icon, query):
        icon.stop()
        self.periodic.closed = True

