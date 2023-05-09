import random
import time
import configparser
from .Util import WhatTheFuckDidYouDo

class LolGame:
    def __init__(self, *, loop=None, connection):
        # Config 
        config = configparser.ConfigParser()
        # Relative paths bad, fix this
        config.read ("../config.ini")
        self.URL = config["DEFAULT"]["URL"] 
        
        # Loop until we get connection
        self.connection = connection

    def list_all(self):
        # List all games
        time.sleep(2)
        self.connection.post("/lol-lobby/v1/custom-games/refresh", data={})
        return self.connection.get("/lol-lobby/v1/custom-games").json()

    def search(self, query):
        # Searches for game by its name
        return [x["id"] for x in self.list_all() if x["lobbyName"] == query]    
            
    def join_by_id(self, id):
        # Joins a game, given an id
        return self.connection.post(f"/lol-lobby/v1/custom-games/{id}/join", data={})

    def join_by_name(self,name):
        # Joins a game given its name
        return self.join_by_id(self.search(str(name)))

    def join_random(self):
        # Joins a random public game
        # mainly debug reasons
        return self.join_by_id(random.choice([x["id"] for x in self.list_all() if not x["hasPassword"]]))
        
        
    def create(self):
        # Creates game
        conn = self.connection
        name = "CustoMM" + str(random.randint(100000, 10000000))
        game = conn.post("/lol-lobby/v2/lobby/", data={
        "customGameLobby": {   
                "configuration": {
                    "gameMode": f"CLASSIC", "gameServerRegion": "", "mapId": 11, "mutators": {"id": 6}, "spectatorPolicy": "AllAllowed", "teamSize": 5
                },
                "lobbyName": name,
                "lobbyPassword": None
            },
            "isCustom": True
        })
        
        return str(name)

    def start(self):
        # Starts champ select
        return self.connection.post("/lol-lobby/v1/lobby/custom/start-champ-select", data={})

    def move(self):
        return self.connection("/lol-lobby/v1/lobby/custom/move-to-lobby", data={})

    def get_team(self):
        # Gets team
        cfg = self.connection.get("/lol-lobby/v2/lobby").json()["gameConfig"]
        return ([x["summonerInternalName"] for x in cfg["customTeam100"]],
                [x["summonerInternalName"] for x in cfg["customTeam200"]]) 