import pystray
from PIL import Image
from .LolScraper import LolScraper
image = Image.open("assets/icon.png")
import pyautogui

class UI:
	
    def __init__(self):
        self.menu = pystray.Menu(
            pystray.MenuItem(
                "Check registration", self.check_registration, default=True
            ),
            pystray.MenuItem(
                "Exit", self.after_click
            )
        )
        self.icon = pystray.Icon("name", image, "CustoMM", self.menu)
        self.icon.run()

    def check_registration(self):
        check = LolScraper().check_summoner()
        if check == "USER_DOES_NOT_EXIST":
            pyautogui.alert("You are not registered, please register on the website.")
        elif check == "UNCLAIMED":
            pyautogui.alert("You have not claimed your account yet, please claim it on discord -> !registed <ACCOUNT_NAME>.")
        elif check[0] == "REGISTRATION_IN_PROGRESS":
            prompt = pyautogui.confirm(f"Your account is currently being registered by {check[1]}, do you want to proceed?")
            if prompt:
                LolScraper().register_summoner(True, check[1])
            else:
                LolScraper().register_summoner(False, check[1])
        else:
            pyautogui.alert(f"Your account is registered to {check[1]['discord']} and your account name is {check[1]['lol']}.")
            
    def after_click(self, icon, query):
        if str(query) == "Exit":
            icon.stop()

