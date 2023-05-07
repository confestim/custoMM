from lcu_connector import Connector 
import asyncio
import requests
import time, sys
import configparser
from .Util import WhatTheFuckDidYouDo

class LolScraper():
    def __init__(self, *, loop=None):
        config = configparser.ConfigParser()
        # Relative paths bad, fix this
        config.read ("../config.ini")
        self.URL = config["DEFAULT"]["URL"] 
        self.connection = Connector(start=True)

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
                print(match)
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
            print("Already up to date, thanks. Program will now close.")
            time.sleep(3)
            sys.exit()
        
        return parsed_matches

    def scrape(self):
        """
        Data scraper for the league client
        """

        # TODO: Check if league is running
        connection = self.connection
        # Summoner 
        summoner = connection.get('/lol-summoner/v1/current-summoner').json()

            
        # Check if account is claimed
        try:
            claimed = requests.get(f"{self.URL}/players/?search={summoner['displayName']}").json()[0]
        except IndexError:
            
            print("User does not exist, register through discord please.")
            print("Program will now close")
            time.sleep(5)
            sys.exit()
        # Case 3: It belongs to nobody and has yet to be claimed.
        if not claimed["discord"]:
            print("This account has not yet been claimed. Please claim it (if its yours) by typing in !claim ACCOUNTNAME to the bot in Discord and running this program again.")
            print(claimed)
            for i in range(10):
                time.sleep(.5)
                sys.stdout.write(".")
                sys.stdout.flush()
                
            sys.exit()
            
        if claimed:
            # Case 1: It belongs to somebody
            if claimed['lol_id'] and claimed['lol']:
                print(f"Welcome, {claimed['discord']}. Thank you for contributing to custoMM!")
                print(claimed)
                print("If this is not you, contact admin.")
                
                # Notify them (if that is the case) that we will do nothing about their new name (slight TODO).
                if claimed['lol'] != summoner['displayName']:
                    print("Ah, you have changed your league handle. Oh well. I will still refer to you with your old one, as this has not been handled properly yet.")
                    
            # Case 2: Registration has begun, but hasn't finished
            elif claimed['lol'] and not claimed['lol_id']:
                prompt = input(f"{claimed['discord']} is trying to claim this account(which you obviously own). Do you want to do that? [y/N]  ")
                if prompt == ("y" or "Y"):
                # TODO: Update api entry
                    account = requests.put(f"{self.URL}/players/{claimed['lol']}/", data={
                    "lol": summoner["displayName"],
                    "lol_id": summoner["puuid"], 
                    "discord_id":claimed["discord_id"],
                    "discord":claimed["discord"]
                    })
                    if account.status_code == 200:
                        print(f"Alright, the account is now yours, {claimed['discord']}.")
                    else:
                        print("Something went wrong when claiming your account...")
                else:
                #TODO: Delete api entry
                    requests.delete(f"{self.URL}/players/{claimed['discord_id']}")
                    print("Okay, deleting the attempt.")
                    sys.exit()
            
            # All cases are covered, everything else will be considered a bug.
            else:
                raise WhatTheFuckDidYouDo()
            
            time.sleep(5)

                

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
            print(req.content)
            if req.status_code == 500:
                print("Serverside error! Contact maintainer!")
                sys.exit()
        print("We have added " + str(len(games)) + " games that were unaccounted for to the db.")
        print("Program will now close.")

        self.connection.stop()
        return True
