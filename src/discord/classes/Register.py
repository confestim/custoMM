from classes.Config import Config
import requests
from classes.Splitter import Splitter

class Register(Splitter):
    def __init__(self, bot, author, ctx, interaction = None, slash=False, player=None):
        super().__init__(bot, author, ctx, interaction, slash)
        self.config = Config()
        self.player = player

    async def register(self):
        """Registers a user to the database: !register <league_name>"""
        config = Config()
        if not self.slash:
            name = " ".join(self.player)
        else:
            name = self.player
        if (len(name) < 4) or (requests.get(f"https://lolprofile.net/summoner/eune/{name}").status_code != 200):
            return await self.send("Provide a normal username (cAsE sEnSiTiVe)")
        league_name = requests.get(f"{config.URL}/players/{name}").json()

        try:
            if not league_name["detail"] == "Not found.":
                return await self.send("Someone already claimed this account")
        except KeyError:
            if league_name["discord_id"]:
                return await self.send(f"{league_name['discord']} has claimed this account.")

        claim_account = requests.post(f"{config.URL}/players/", data={
            "discord": self.author,
            "discord_id": self.author.id,
            "lol": name
        })

        if not claim_account.json().get('discord_id') and claim_account.json().get("lol"):

            # In case that account doesn't exist at all
            claim_account = requests.put(f"{config.URL}/players/{name}/", data={
                "discord": self.author.name,
                "discord_id": self.author.id,
                "lol": name
            })
            print(claim_account.content)

        # TODO: In case the account exists, but not yet claimed

        print(claim_account.status_code)
        if claim_account.status_code == 201 or claim_account.status_code == 200:
            return await self.send("Success, now approve from client")
        return await self.send("Something went wrong...")