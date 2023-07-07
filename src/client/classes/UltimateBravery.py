from requests import get
from random import randint 
from collections import Counter

# TODO: Implement version check, which increases BOTTOM_END and TOP_END if the version is not the same as the current one
BOTTOM_END = 45000000
TOP_END = 45999999
VERSION = [13,13,1]
class UltimateBravery:
    

    def __init__(self, seed=randint(BOTTOM_END, TOP_END), role=None):
        
        self.seed = seed       
        self.data = self.__getRandom()
        self.version = self.data.get("version").split(".")
        self.role = role
        if Counter(VERSION) != Counter([int(x) for x in self.version]):
            raise NameError("Version mismatch! Program needs to be updated.")

    

    def __getRandom(self):
        data = get(f"https://api2.ultimate-bravery.net/bo/api/ultimate-bravery/v1/classic/dataset/seed/{self.seed}?language=en").json()
        
        while data.get("status") != "success" and (data.get("data").get("role") != self.role) if self.role else None:
            print(str(self.seed) + " doesn't work")
            self.seed = randint(BOTTOM_END, TOP_END)
            data = get(f"https://api2.ultimate-bravery.net/bo/api/ultimate-bravery/v1/classic/dataset/seed/{self.seed}?language=en").json()

        return data.get("data")

        
    @property
    def raw_data(self):
        return self.data

    @property
    def champion(self):
        return self.data.get("champion").get("name")
    
    @property
    def spell(self):
        return self.data.get("champion").get("spell").get("key")
    
    @property
    def items(self):
        return self.data.get("items")
    
    @property
    def summonerSpells(self):
        return self.data.get("summonerSpells")
    
    @property
    def runes(self):
        return self.data.get("runes")
    
    @property
    def role(self):
        return self.data.get("role")
    
    @property 
    def itemSet(self):
        return self.data.get("itemSet")

