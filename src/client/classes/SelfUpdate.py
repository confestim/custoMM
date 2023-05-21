from requests import get, put, post, delete
from wget import download
from os import system, path
from time import sleep
from logging import info
from .Notify import Notify

class SelfUpdate():
    """Checks for new updates and prompts user to install

        Args:
            version (str): Version number
            base_dir(str): Base dir of program
    """
    def __init__(self, version:str, base_dir:str):
        
        self.version = version
        self.newest = get("https://api.github.com/repos/confestim/custoMM/releases/latest").json()["tag_name"]
        self.new_version = False
        if self.version != self.newest:
            self.new_version = True
        return
    
    def update(self):
        """ Updater
        """
        download(f"https://github.com/confestim/custoMM/releases/download/{self.newest}/custoMM_installer.exe")
        system("custoMM_installer.exe")