from requests import get, put, post, delete
from wget import download
from os import system
from time import sleep

class SelfUpdate():
    # Auto update when new release is found on github
    def __init__(self, version, ui):
        self.version = version
        self.newest = get("https://api.github.com/repos/confestim/custoMM/releases/latest").json()["tag_name"]
        if self.version != self.newest:
            ui.icon.notify("New version found", f"New version {newest} found, updating...", title="CustoMM")
            sleep(5)
            self.update()
        return
    
    def update(self):
        download(f"https://github.com/confestim/custoMM/releases/download/{self.newest}/custoMM_installer.exe")
        system("custoMM_installer.exe")