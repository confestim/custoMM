from lcu_driver import Connector
import requests

# Change this when new champ(Rito are fucking stupid)
VERSION = "13.5.1"

# Init connection
connector = Connector()

def parse_history(history:dict) -> list:
    # Parses current player's history
    # Input: Logged in player's match history
    # Output: ID's of custom games, ready to send to server
    
    # Get the entirety of the current champs and their ids
    
    champs = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{VERSION}/data/en_US/champion.json").json()["data"]
    # TODO: Host a champs dict in the form of {ID: NAME}
    for i in history["games"]["games"]:
       if i["gameType"] == "CUSTOM_GAME":
    # TODO: Format this list in the form of [{gid: GAME-ID, puuid:puuid}]
    
    
# Get current summoner
@connector.ready
async def connect(connection):
    summoner = await connection.request('get', '/lol-summoner/v1/current-summoner')
    summoner = await summoner.json()
    print(f"Getting data for {summoner['displayName']}, with ID: {summoner['puuid']}")
    match_history = await connection.request('get', '/lol-match-history/v1/products/lol/current-summoner/matches?endIndex=100')
    match_history = await match_history.json()

    parse_history(match_history)
    
@connector.close
async def disconnect(connection):
    print('Finished task')



    
   
    


connector.start()
