import discord
from discord.ext import commands
from .Splitter import Splitter
from .Config import Config
import requests

class Leaderboard(Splitter):
    
    def __init__(self, bot, players:int, author=None, ctx=None, interaction=None, slash=False):
        # Inherits send function from Splitter
        super().__init__(bot, author, ctx, interaction, slash)
        self.players = players
        
    async def leaderboard(self):
        """Shows the Top <players> leaderboard: !leaderboard <number_of_players> <max>"""
        config = Config()
        leaderboard = requests.get(f"{config.URL}/players").json()
    
        if len(leaderboard) < self.players:
            return await self.send(f"We don't have that many self.players in the database. We have {len(leaderboard)}.")

        leaderboard = leaderboard[:self.players]
        embed = discord.Embed(title=f"Top {self.players} players", description="Ordered by mmr", color=0xFF5733)
        embed.set_author(name="custoMM", icon_url="https://git.confest.im/boyan_k/custoMM/raw/branch/main/images/smol_logo.png")
        fields = [embed.add_field(name=x['lol'], value=x['mmr']) for x in leaderboard]
        return await self.send(message=None, embed=embed)

    