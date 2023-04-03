from lcu_driver import Connector
import requests
# Create config.py when running for the first time
import config
import asyncio
import json
import time, sys

import random 

# Test connection to server

try:
    test = requests.get(config.SITE_URL).json()

except Exception:
    # NEVER DO THIS
    # although, what could go wrong...
    print("Server seems to be down, please contact admin if it keeps doing this")
    sys.exit()


# needed for windows
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Init connection
connector = Connector()

class WhatTheFuckDidYouDo(Exception):
    # We raise this when we don't know what the fuck happened
    def __init__(self, message="Congrats, you broke this program, please explain your steps as an issue at https://github.com/confestim/custoMM"):
        self.message = message
        super().__init__(self.message)


def calculate_kda(kills:int, assists:int, deaths:int):
    if deaths == 0:
        deaths = 1
    return round((kills+assists)/deaths, 3)


async def parse_history(connection, history:dict, old_ids:list) -> list:
    # Parses current player's history
    # Input: Logged in player's match history
    # Output: New data about unaccounted for custom games, ready to send to server
    """
    {
    "game_id": "12345",
    "participants": {
        "t1": {
        "won":true,
        "summoners": [
            {
            "name": "summoner",
            "kda": 0.333,
            },
        ]
        }
        },
        "t2": {
        "won":false,
        "summoners": {
            ...
        }
        }
    }
    }
    """
    parsed_matches = []
    new = 0
    for i in history["games"]["games"]:
       if i["gameType"] == "CUSTOM_GAME" and str(i["gameId"]) not in old_ids:
            
            new += 1
            match = await connection.request('get', f'/lol-match-history/v1/games/{i["gameId"]}')
            match = await match.json()
            #print(match)
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
                    parsed_match["participants"]["t1"]["summoners"].append({"name":match["participantIdentities"][player]["player"]["summonerName"], "kda": calculate_kda(kills, assists, deaths)})
                else:
                    parsed_match["participants"]["t2"]["summoners"].append({"name":match["participantIdentities"][player]["player"]["summonerName"], "kda": calculate_kda(kills, assists, deaths)})
            parsed_matches.append(parsed_match)
    if not new:
        print("Already up to date, thanks.")
        sys.exit()
    return parsed_matches
    
    # TODO: Format this list in the form of [{gid: GAME-ID, puuid:puuid}]
    
    
# Get current summoner
@connector.ready
async def connect(connection):
    # Summoner 
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    summoner = await summoner.json()
    
       
    # Check if account is claimed
    try:
        claimed = requests.get(config.SITE_URL+ f"players/?search={summoner['displayName']}").json()[0]
    except IndexError:
        
        print("User does not exist, register through discord please.")
        sys.exit()
    
    if claimed:
        # Case 1: It belongs to somebody
        if claimed['lol_id'] and claimed['lol']:
            print(f"Welcome, {claimed['discord']}. Thank you for contributing to custoMM!")
            print("If this is not you, contact admin.")
            
            # Notify them (if that is the case) that we will do nothing about their new name (slight TODO).
            if claimed['lol'] != summoner['displayName']:
                print("Ah, you have changed your league handle. Oh well. I will still refer to you with your old one, as this has not been handled properly yet.")
                
        # Case 2: Registration has begun, but hasn't finished
        elif claimed['lol'] and not claimed['lol_id']:
            prompt = input(f"{claimed['discord']} is trying to claim this account(which you obviously own). Do you want to do that? [y/N]  ")
            if prompt == ("y" or "Y"):
            # TODO: Update api entry
                account = requests.put(config.SITE_URL + f"players/{claimed['discord_id']}/", data={
                "lol": summoner["displayName"],
                "lol_id": summoner["puuid"], 
                "discord_id":claimed["discord_id"],
                "discord":claimed["discord"]
                })
                print(account.content)
                if account.status_code == 200:
                    print(f"Alright, the account is now yours, {claimed['discord']}.")
                else:
                    print("Something went wrong when claiming your account...")
            else:
            #TODO: Delete api entry
                requests.delete(config.SITE_URL + f"players/{claimed['discord_id']}")
                print("Okay, deleting the attempt.")
                sys.exit()
        
        # All cases are covered, everything else will be considered a bug.
        else:
            raise WhatTheFuckDidYouDo()
    
    # Case 3: It belongs to nobody and has yet to be claimed.
    else:
        print("This account has not yet been claimed. Please claim it (if its yours) by typing in !claim ACCOUNTNAME to the bot in Discord and running this program again.")
        for i in range(10):
            time.sleep(.5)
            sys.stdout.write(".")
            sys.stdout.flush()
            
        sys.exit()
            
    
    # Match History
    match_history = await connection.request('get', '/lol-match-history/v1/products/lol/current-summoner/matches?endIndex=99')
    match_history = await match_history.json()
  
    # Stage old ids in order for them to be parsed
    old_ids = requests.get(config.SITE_URL + "games/").json()
    old_ids = [x["game_id"] for x in old_ids]


    # TODO: Optimize the process of acquisition of new matches 
    games = await parse_history(connection, match_history, old_ids)
            
    # Post the new games to your server(change in config.py)
    for i in games:
        req = requests.post(config.SITE_URL + "games/", json=i)
        print(req.content)
        if req.status_code == 500:
            print("Serverside error! Contact maintainer!")
            sys.exit()
    print("We have added " + str(len(games)) + " games that were unaccounted for to the db.")
    
@connector.close
async def disconnect(connection):
    print('Harvesting is over!')
    
# Begin

connector.start()


