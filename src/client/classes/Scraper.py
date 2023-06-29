# League of Legends Client API Wrapper
from lcu_connector import Connector
from lcu_connector.exceptions import ClientProcessError, MissingLockfileError
# TODO: Bug when trying to access previous lockfile

# Logging
from logging import info, error
# Requests
from requests import get,put,post,delete
from requests.exceptions import ConnectionError

# Custom imports
from .Exceptions import RegistrationError
from .Game import Game
from .Notify import Notify

# Config
from configparser import ConfigParser

from time import sleep
from json import dumps

TIME_DELAY = 20
GAMES_TO_SCRAPE = 1000

class Scraper:
    """ Scraper

    Args:
        config (ConfigParser): Config instance
        base_dir (str): Base dir of program
    """
    
    def __init__(self, *, config:ConfigParser, base_dir:str):

        # Config
        self.config = config
        self.URL = self.config["DEFAULT"]["URL"] 
        self.connection = None
        self.base_dir = base_dir

        # Loop until we get connection or user closes the polling program
        self.conn = self.get_connection()
        if not self.conn:
            return
        
        # Get current summoner
        self.summoner = self.connection.get('/lol-summoner/v1/current-summoner').json()
        self.name = self.summoner["displayName"]

    def get_connection(self):
        """ Tries to get connnection with local LCU.
        Returns:
            bool: Connection failed or established
        """
        notification = Notify(base_dir=self.base_dir)
        while not self.connection:
            try:
                self.connection = Connector()
                self.connection.start()
            except ClientProcessError or MissingLockfileError:
                if notification.exit:
                    return False
                info("Polling...")
                notification.notification("custoMM is waiting for LoL to start in the background.")
                notification.notified = True
                sleep(TIME_DELAY)
          
        notification.quit()
        return True

    def calculate_kda(self, kills:int, assists:int, deaths:int, decimals:int=3):
        """ Calculates KDA ratio

        Args:
            kills (int): Kills
            assists (int): Assists
            deaths (int): Deaths
            decimals (int,optional): Decimal points to round to. Defaults to 3.

        Returns:
            float: rounded
        """
        if deaths == 0:
            deaths = 1
        return round((kills+assists)/deaths, decimals)

    def parse_history(self, history:dict, old_ids:list) -> list:
        """Parses current player's history

        Args:
            history (dict): Current player's history
            old_ids (list): Cached games (on server)

        Returns:
            list: Serialized games ready for the server
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
            # Notify player that we're up to date
            sleep(3)
            
        
        return parsed_matches

    def register_summoner(self, claim:bool, claimed):
        """Attempts to register the current summoner

        Args:
            claim (bool): Register or Deregister(Delete)
            claimed (dict): Claimed user data ["lol", "lol_id", "discord", "discord_id"]
        """
        if claim:
            account = put(f"{self.URL}/players/{claimed['lol']}/", data={
                "lol": claimed["lol"],
                "lol_id": claimed["lol_id"], 
                "discord_id":claimed["discord_id"],
                "discord":claimed["discord"]
            })
            if account.status_code == 200:
                Notify(base_dir=self.base_dir, exit_after=True).notification(f"Alright, the account is now yours, {claimed['discord']}.")
            else:
                Notify(base_dir=self.base_dir, exit_after=True).notification("Something went wrong when claiming your account...")
        else:
            delete(f"{self.URL}/players/{claimed['discord_id']}")


    def check_summoner(self):
        """
        Checks if logged in summoner is registered
        """

        connection = self.connection
        # Summoner 

            
        # Check if account is claimed
        try:
            claimed = get(f"{self.URL}/players/?search={self.summoner['displayName']}").json()[0]
        except Exception as e:
            error(e) 
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
                raise RegistrationError()

    def move_needed(self, checker, game:Game, name:str):
        """ Moves player into other team if needed

        Args:
            checker (dict): Information about the remote current game, we need the teams.
            game (Game): Local game instance
            name (str): Username we're looking for
        """
        
        # This is buggy, try to find a better way to do this.
        # Like for example, letting team 1 pass first, and then team 2.
        local_teams = game.get_teams()
        checker = checker["teams"]
        if name in local_teams[0] and not name in checker[0]:
            game.move()
            info("Moving to Team 2")
        elif name in local_teams[1] and not name in checker[1]:
            game.move()
            info("Moving to Team 1")

    def start(self, checker, game:Game, timeout:int=120):
        """ Waits for 10 players and starts game

        Args:
            checker (dict): Information about current game (http://yourser.ver/current/)
            game (Game): Local game instance
            timeout (int, optional): Timeout for lobby in seconds
        """
        # Move if needed
        self.move_needed(checker, game, self.name)
        timeout_counter = 0
        
        # Wait until 10 players
        while response := get(f"{self.URL}/current/{self.name}").json()["players"] != 10:
            info("Waiting for players...")
            timeout_counter += 5
            if timeout_counter == timeout:
                Notify(base_dir=self.base_dir, exit_after=True).notification(message="Timed out, not enough players joined, leaving.")
                break
            sleep(5)

        # Start or leave
        if response == 10:
            Notify(base_dir=self.base_dir, exit_after=True).notification("Starting game...")
            game.start()
        else:
            game.leave()
        
        # Current game gets deleted either way
        sleep(30)
        delete(f"{self.URL}/current/{self.name}")

    def check_for_game(self):
        """
        Checks if a game is going on right now.
        """
        # Initial check
        try:
            checker = get(f"{self.URL}/current").json()[0]
        except Exception:
            return "NO_GAME"
        if checker["lobby_name"] == "null":
            return
        # Local game instance
        game = Game(connection=self.connection, config=self.config)
        
        # Check if inside the game already
        if game.in_game_with_name(checker["lobby_name"]):
            game.leave_with_creator(checker["creator"])
            return "JOINED"
        
        # If you are the creator, create the game and disclose its name to the server
        if checker["creator"] == self.name:
            Notify(base_dir=self.base_dir, exit_after=True).notification("You are the creator! Creating lobby...")
            created = game.create() 
            # TODO: DEBUG
            r = put(f"{self.URL}/current/{self.name}/", data={
                "lobby_name": created,
                "creator": self.name,
                "players": 1,
                "teams": dumps(checker["teams"], indent=4)
                })
            

            # Start the game
            self.start(checker, game)
            return "CREATED"
 
        else:
            # If you have to join
            try:
                name = checker["lobby_name"]
            except KeyError:
                # Wait until lobby name becomes available
                while not get(f"{self.URL}/current").json()[0].get("lobby_name"):
                    sleep(10)
                checker = get(f"{self.URL}/current").json()
                name = checker["lobby_name"]
            Notify(base_dir=self.base_dir, exit_after=True).notification(f"Joining {name}...")

            # Join the lobby and move if needed
            game.join_by_name(name)
            self.move_needed(checker, game, self.name)
            
            # Update count of players         
            put(f"{self.URL}/current/{checker['creator']}/", data={
                "lobby_name": checker["lobby_name"],
                "creator": name,
                "players": int(checker["players"])+1,
                "teams": dumps(checker["teams"], indent=4)

            })
            return "JOINED" 
        
 
    def scrape(self):
        """Scrapes current account and sends it to server"""
       
        try:
            connection = self.connection
            self.check_summoner()
            # Match History
            match_history = connection.get(f'/lol-match-history/v1/products/lol/current-summoner/matches?endIndex={GAMES_TO_SCRAPE}')
            match_history = match_history.json()

            # Stage old ids in order for them to be parsed
            old_ids = get(f"{self.URL}/games/").json()
            old_ids = [x["game_id"] for x in old_ids]


            # TODO: Optimize the process of acquisition of new matches 
            games = self.parse_history(match_history, old_ids)
                    
            # Post the new games to your server(change in config.json)
            for i in games:
                req = post(f"{self.URL}/games/", json=i)
                if req.status_code == 500:
                    Notify(base_dir=self.base_dir, exit_after=True).notification("Serverside error! Contact maintainer!")
                    
            return len(games)

        # If client is not opened, destroy past connection and try to get new one
        except ConnectionError:
            self.connection = None
            self.get_connection()
