from lcu_connector import Connector
from lcu_connector.exceptions import ClientProcessError
import logging
import requests
import time, sys
import json
import configparser
from .Util import WhatTheFuckDidYouDo
from .Game import Game

class Scraper:
    def __init__(self, *, loop=None, ui=None):
        self.ui = ui
        self.config = configparser.ConfigParser()
        # Relative paths bad, fix this
        self.config.read ("../config.ini")
        self.URL = self.config["DEFAULT"]["URL"] 
        # Loop until we get connection
        self.connection = None
        
        while not self.connection:
            try:
                self.connection = Connector()
                self.connection.start()
            except ClientProcessError:
                print("League client not open, sleeping...")
                time.sleep(90)
        self.summoner = self.connection.get('/lol-summoner/v1/current-summoner').json()
        self.name = self.summoner["displayName"]

    def calculate_kda(self, kills:int, assists:int, deaths:int):
        """
        Calculates kill, death, assist ratio
        Input: kills, assists, deaths
        Output: KDA ratio
        """
        if deaths == 0:
            deaths = 1
        return round((kills+assists)/deaths, 3)

    def parse_history(self, history:dict, old_ids:list) -> list:
        """
        Parses current player's history
        Input: Logged in player's match history
        Output: New data about unaccounted for custom games, ready to send to server
        """
        
        connection = self.connection
              

        parsed_matches = []
        new = 0
        for i in history["games"]["games"]:
          if i["gameType"] == "CUSTOM_GAME" and str(i["gameId"]) not in old_ids and not i["gameMode"] == "PRACTICETOOL":
                
                new += 1
                match = connection.get(f'/lol-match-history/v1/games/{i["gameId"]}').json()
                parsed_match = {
                            "game_id": match["gameId"],
                            "participants": {
                                "t1": {
                                    "won": True if match["teams"][0]["win"] == "Won" else False,
                                    "summoners": []
                                },
                                "t2": {
                                    "won": True if match["teams"][1]["win"] == "Won" else False,
                                    "summoners": []
                                }
                            }
                }
                
                # Sloppy solution, find fix.
                print("Extracting data...")
                for player in range(10):
                    current_player = match["participants"][player]["stats"]
                    kills = current_player["kills"]
                    assists = current_player["assists"]
                    deaths = current_player["deaths"]
                    if player <= 5:
                        parsed_match["participants"]["t1"]["summoners"].append({"name":match["participantIdentities"][player]["player"]["summonerName"], "kda": self.calculate_kda(kills, assists, deaths)})
                    else:
                        parsed_match["participants"]["t2"]["summoners"].append({"name":match["participantIdentities"][player]["player"]["summonerName"], "kda": self.calculate_kda(kills, assists, deaths)})
                parsed_matches.append(parsed_match)
        if not new:
            print("Already up to date.")
            time.sleep(3)
            
        
        return parsed_matches

    def register_summoner(self, claim, claimed):
        if claim:
            account = requests.put(f"{self.URL}/players/{claimed['lol']}/", data={
                "lol": claimed["lol"],
                "lol_id": claimed["lol_id"], 
                "discord_id":claimed["discord_id"],
                "discord":claimed["discord"]
            })
            if account.status_code == 200:
                print(f"Alright, the account is now yours, {claimed['discord']}.")
            else:
                print("Something went wrong when claiming your account...")
        else:
            requests.delete(f"{self.URL}/players/{claimed['discord_id']}")


    def check_summoner(self):
        """
        Checks if summoner is registered
        """

        connection = self.connection
        # Summoner 

            
        # Check if account is claimed
        try:
            claimed = requests.get(f"{self.URL}/players/?search={self.summoner['displayName']}").json()[0]
        except Exception as e:
            print(e) 
            return "USER_DOES_NOT_EXIST"
            
        # Case 1: It belongs to nobody and has yet to be claimed.
        if not claimed["discord"]:
            return "UNCLAIMED"
            
        if claimed:
            # Case 2: It belongs to somebody
            if claimed['lol_id'] and claimed['lol']:
                    
                # Change name in db if different in-game
                if claimed['lol'] != self.summoner['displayName']:
                    self.register_summoner(True, claimed)
                
                return (claimed['discord'], claimed['lol'])
                    
            # Case 3: Registration has begun, but hasn't finished
            elif claimed['lol'] and not claimed['lol_id']:
               claimed["lol_id"]=self.summoner["puuid"]
               return ["REGISTRATION_IN_PROGRESS", claimed]                  
                
            # All cases are covered, everything else will be considered a bug.
            else:
                raise WhatTheFuckDidYouDo()

    def move_needed(self, checker, game, name):
        # Move if you have to
        
        # This is buggy, try to find a better way to do this.
        # Like for example, letting team 1 pass first, and then team 2.
        local_teams = game.get_teams()
        
        if name in local_teams[0] and not name in checker["teams"][0]:
            game.move()
            logging.info("Moving to Team 2")
        elif name in local_teams[1] and not name in checker["teams"][1]:
            game.move()
            logging.info("Moving to Team 1")

    def start(self, checker, game):
        self.move_needed(checker, game, self.name)
        time.sleep(5)
        # Wait until there are 10 players(confirmed) in the lobby
        timeout_counter = 0
        while response := requests.get(f"{self.URL}/current/{self.name}").json()["players"] != 10:
            logging.info("Waiting for players...")
            timeout_counter += 5
            if timeout_counter == 60:
                logging.info("Timeout, aborting...")
                break
            time.sleep(5)
        if response == 10:
            logging.info("Starting game...")
            game.start()
        else:
            game.leave()
        requests.delete(f"{self.URL}/current/{self.name}")

    def check_for_game(self):
        """
        Checks if a game is going on right now.
        """
        try:
            checker = requests.get(f"{self.URL}/current").json()[0]
        except IndexError:
            return "NO_GAME"
        game = Game(connection=self.connection)
        
        # If you are indeed the creator, create the game and disclose its name to the server
        if checker["creator"] == self.name:
            created = game.create() 
            # TODO: DEBUG
            print(checker["teams"])
            r = requests.put(f"{self.URL}/current/{self.name}/", data={
                "lobby_name": created,
                "creator": self.name,
                "players": 1,
                "teams": json.dumps(checker["teams"], indent=4)
                })
            print(r.content)
            

            # Start the game
            self.start(checker, game)
            return "CREATED"
 
        else:
            # If you have to join
            try:
                name = checker["lobby_name"]
            except KeyError:
                # Wait until lobby name becomes available
                while not requests.get(f"{self.URL}/current").json()[0].get("lobby_name"):
                    time.sleep(10)
                checker = requests.get(f"{self.URL}/current").json()
                name = checker["lobby_name"]
   
            # Join the lobby
            game.join_by_name(name)

            # Update count of players         
            requests.put(f"{self.URL}/current/{checker['creator']}", data={
                "lobby_name": checker["lobby_name"],
                "creator": name,
                "players": int(checker["players"])+1,
                "teams": json.dumps(checker["teams"], indent=4)

            })
            return "JOINED" 
        
 
        


    def scrape(self):
        """Scrapes current account and sends it to server"""
        
        connection = self.connection
        self.check_summoner()
        # Match History
        match_history = connection.get('/lol-match-history/v1/products/lol/current-summoner/matches?endIndex=99')
        match_history = match_history.json()

        # Stage old ids in order for them to be parsed
        old_ids = requests.get(f"{self.URL}/games/").json()
        old_ids = [x["game_id"] for x in old_ids]


        # TODO: Optimize the process of acquisition of new matches 
        games = self.parse_history(match_history, old_ids)
                
        # Post the new games to your server(change in config.json)
        for i in games:
            req = requests.post(f"{self.URL}/games/", json=i)
            if req.status_code == 500:
                print("Serverside error! Contact maintainer!")
                
        return len(games)
