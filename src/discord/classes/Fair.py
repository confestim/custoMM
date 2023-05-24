import requests
from .Splitter import Splitter
import discord
from discord.ext import commands
import asyncio
from urllib.parse import quote
from random import choice
from json import dumps

class Fair(Splitter):
    def __init__(self, bot,author:discord.Member, ctx:commands.Context=None, interaction:discord.Interaction=None, slash=False):
        super().__init__(bot, author, ctx, interaction, slash)
        
        if slash:
          splitter = Splitter(bot=bot, author =author, interaction=interaction, slash=True)
        else:
          splitter = Splitter(bot=bot, author =author, ctx=ctx)
   
   
    async def divide(self):
        players = await self.ready()
        if not players:
            return

        valid_players = []

        # This does not support multiple accounts, refer to issue #7
        # Initial check for existing players
        for i in players:

            player = requests.get(f"{self.config.URL}/players/?search={i.id}").json()
            if not player:
                await self.send(f"<@{i.id}> has no league account associated with their name. Please register in order to calculate MMR more accurately.")
            else:
                valid_players.append(player[0]["lol"])

        # If not enough players, return
        if len(valid_players) < 10:
            return await self.send("Couldn't create fair game. Whoever isn't registered, please do.")

        # Getting the players
        query_string = "?"+"&".join(["players={}".format(quote(player)) for player in valid_players])
        print(query_string)
        teams = requests.get(
            f"{self.config.URL}/game/?{query_string}")

        # Second check for existing players
        # Also, funny status code
        if teams.status_code == 451:
            for i in teams.content:
                await self.send(f"{i} has not been found by the API. Please register in order to calculate MMR more accurately.")
            return
        
        teams = teams.json()
        # TODO: Debug, remove
        print(teams)
        
        await self.split(teams[0], teams[1], fair=True)

        # Create current game
        requests.post(f"{self.config.URL}/current/", data={
            "lobby_name": None,
            "players": 0,
            "creator": choice(valid_players),
            "teams": dumps(teams)
        })


        return
