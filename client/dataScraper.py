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
    
    # Get the entirety of the current champs and their ids
    matches = []
    ids = [] 
    for i in history["games"]["games"]:
       if i["gameType"] == "CUSTOM_GAME" and i["gameId"] not in old_ids:
  
            match = await connection.request('get', f'/lol-match-history/v1/games/{i["gameId"]}')
            matches.append(await match.json())
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
    except KeyError:
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
                requests.put(config.SITE_URL + f"players/{claimed['discord_id']}", data={"lol": summoner["displayName"], "lol_id": summoner["puuid"]})
                print(f"Alright, the account is now yours, {claimed['discord']}.")
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
  
    
    # PLACEHOLDER
    # TODO: Do communication b/n client and server which provides IDs of already cached games in a list 
    requests.get(config.SITE_URL)
    old_ids = []  
    games = await parse_history(connection, match_history, old_ids)
    
    
        
    print("We have added " + str(len(games)) + " games that were unaccounted for to the db.")
    
    # TODO: Create a separate table with the game info
    # Also find what we need from each game (or in other words, figure out the algo by which we will calculate MMR)
    
    
    # Post the new games to your server(change in config.py)
    #for i in games:
        # TODO: finish this post request
      ##  requests.post(config.SITE_URL + "games/", data={"id": i["gameId"] )
    
@connector.close
async def disconnect(connection):
    print('Harvesting is over!')
    
# Begin

connector.start()


