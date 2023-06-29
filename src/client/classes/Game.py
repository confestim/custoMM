from random import choice, randint
from time import sleep
from logging import info

class Game:
    def __init__(self, *, loop=None, connection,config):
        self.password = str(config["LEAGUE"]["LOBBY_PASS"])
        # Loop until we get connection
        self.connection = connection

    def list_all(self):
        # List all games
        sleep(1)
        self.connection.post("/lol-lobby/v1/custom-games/refresh", data={})
        return self.connection.get("/lol-lobby/v1/custom-games").json()

    def search(self, query):
        # Searches for game by its name
        return [x["id"] for x in self.list_all() if x["lobbyName"] == query]    
            
    def join_by_id(self, id):
        # Joins a game, given an id
        return self.connection.post(f"/lol-lobby/v1/custom-games/{id}/join", data={"password":self.password})

    def join_by_name(self,name):
        # Joins a game given its name
        try:
            return self.join_by_id(self.search(str(name))[0])
        except IndexError:
            info("Game not found, try again.")
            

    def join_random(self):
        # Joins a random public game
        # mainly debug reasons
        return self.join_by_id(choice([x["id"] for x in self.list_all() if not x["hasPassword"]]))
        
    def in_game_with_name(self, lobby_name):
        try:
            name = self.connection.get("/lol-lobby/v2/lobby").json()["gameConfig"]["customLobbyName"]
            if lobby_name == name:
                return True
        except Exception as e:
            info(e)
        return False

    def leave_with_creator(self, creator):
        members = [x["summonerName"] for x in self.connection.get("/lol-lobby/v2/lobby/").json()["members"]]
        if creator not in members:
            self.leave()
        
    def create(self):
        # Creates game
        conn = self.connection
        name = "CustoMM " + str(randint(100000, 10000000))
        game = conn.post("/lol-lobby/v2/lobby/", data={
        "customGameLobby": {   
                "configuration": {
                    "gameMode": f"CLASSIC", "gameServerRegion": "", "mapId": 11, "mutators": {"id": 6}, "spectatorPolicy": "AllAllowed", "teamSize": 5
                },
                "lobbyName": name,
                "lobbyPassword": self.password
            },
            "isCustom": True
        })
        
        return str(name)

    def start(self):
        # Starts champ select
        return self.connection.post("/lol-lobby/v1/lobby/custom/start-champ-select", data={})

    def move(self):
        return self.connection.post("/lol-lobby/v1/lobby/custom/switch-teams", data={})

    def leave(self):
        return self.connection.delete("/lol-lobby/v2/lobby")

    def get_teams(self):
        # Gets team
        cfg = self.connection.get("/lol-lobby/v2/lobby").json()["gameConfig"]
        return [[x["summonerInternalName"] for x in cfg["customTeam100"]],
                [x["summonerInternalName"] for x in cfg["customTeam200"]]]
        