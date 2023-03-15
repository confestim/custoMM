from lcu_driver import Connector
import requests
# Create config.py when running for the first time
import config


# Init connection
connector = Connector()

def parse_history(history:dict, old_ids:list) -> list:
    # Parses current player's history
    # Input: Logged in player's match history
    # Output: ID's of custom games, ready to send to server
    
    # Get the entirety of the current champs and their ids
    new_games = []
    for i in history["games"]["games"]:
       if i["gameType"] == "CUSTOM_GAME" and i["gameId"] not in old_ids:
           new_games.append(i)
    return new_games
    # TODO: Format this list in the form of [{gid: GAME-ID, puuid:puuid}]
       
    
# Get current summoner
@connector.ready
async def connect(connection):
    # Summoner 
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    summoner = await summoner.json()
    
    # DEBUG
    print(f"Getting data for {summoner['displayName']}, with ID: {summoner['puuid']}")
    print(summoner)
    # ------
    
    # Match History
    match_history = await connection.request('get', '/lol-match-history/v1/products/lol/current-summoner/matches?endIndex=100')
    match_history = await match_history.json()
    
    # PLACEHOLDER
    # TODO: Do communication b/n client and server which provides IDs of already cached games in a list 
    requests.get(config.SITE_URL)
    old_ids = [] 
    games = parse_history(match_history, old_ids)
    
    
    # Post a request to your server(change in config.py)
    
    
@connector.close
async def disconnect(connection):
    print('Finished task')
    
# Begin
connector.start()


