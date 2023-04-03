from lcu_driver import Connector
import requests
# Create config.py when running for the first time
import config
import asyncio
import json
import time, sys

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
    matches = []
    ids = [] 
    for i in history["games"]["games"]:
       if i["gameType"] == "CUSTOM_GAME" and i["gameId"] not in old_ids:
  
            match = await connection.request('get', f'/lol-match-history/v1/games/{i["gameId"]}')
            match = await match.json()
            match = {
                        "game_id": match["metadata"]["matchId"],
                        "participants": {
                            "t1": {
                                "won": match["teams"][0]["win"],
                                "summoners": [{"name":x["summonerName"], "kda":int(x["kda"])} if x["teamId"] == match["teams"][0]["teamID"] for x in match["info"]["participants"]]
                            }
                            "t2": {
                                "won": match["teams"][1]["win"],
                                "summoners": [{"name":x["summonerName"], "kda":int(x["kda"])} if x["teamId"] == match["teams"][1]["teamID"] for x in match["info"]["participants"]]
                            }
                        }
            }
            matches.append(match)
    if not ids:
        print("Already up to date, thanks.")
        sys.exit()
    return matches
    
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
    except Exception as e:
        if e == "IndexError":
            print("User does not exist")
            pass
        print("Maybe open up your League client?")
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
    old_ids = requests.get(config.SITE_URL + "/games/").json()
    old_ids = [x["game_id"] for x in old_ids]

    # TODO: Optimize the process of acquisition of new matches 
    games = await parse_history(connection, match_history, old_ids)
            
    # Post the new games to your server(change in config.py)
    for i in games:
        requests.post(config.SITE_URL + "games/", data=i)
    print("We have added " + str(len(games)) + " games that were unaccounted for to the db.")
    
@connector.close
async def disconnect(connection):
    print('Harvesting is over!')
    
# Begin

connector.start()


