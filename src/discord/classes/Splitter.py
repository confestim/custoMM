from .Config import Config
import discord
from discord.ext import commands
import asyncio
from typing import List
import random

class Splitter:
    def __init__(self, 
                 bot:commands.Bot, 
                 author:discord.Member,
                 ctx:commands.Context=None, 
                 interaction:discord.Interaction=None,
                 slash=False):
        # Config
        self.ctx = ctx
        self.interaction = interaction
        self.config = Config()
        self.bot = bot
        self.author = author
        self.slash = slash
        self.responses = 0

    async def send(self, message, embed=None):
        if not self.slash and self.ctx is not None:
            return await self.ctx.send(message, embed=embed)
        self.responses += 1
        if self.responses > 1:
            return await self.interaction.followup.send(message, embed=embed)
        return await self.interaction.response.send_message(message, embed=embed)
    
    async def ready(self):

        """
        Checks if players are ready to be split
        """

        # Fetching user channel
        try:
            channel = self.bot.get_channel(self.author.voice.channel.id)
        except AttributeError:
            await self.send("You think you're cool or something? Get in a channel first.")
            return False

        players = channel.members
        if len(players) < 10:
            await self.send(f"Get more people in ({len(players)}/10)")
            return False

        if len(players) % 10 != 0:
        # If total players not divisible by 10, can't split
            await self.send("Can't split(remove bots and non-players)")
            return False
        
        return players     
      
    async def split(self, players_1, players_2, fair=False):
        """
        Splits players into 2 teams
        """
        # Declaring channels
        team_1 = discord.utils.get(self.config.team_1)
        team_2 = discord.utils.get(self.config.team_2)
        print(team_1, team_2)
        # Embedding
        one_em = discord.Embed(title=f"Team 1", colour=discord.Colour(0x8c0303))
        two_em = discord.Embed(title=f"Team 2", colour=discord.Colour(0x0B5394))
        
        # Format if fair
        if fair:
            players_1 = [await self.bot.fetch_user(x["discord_id"]) for x in players_1]
            players_2 = [await self.bot.fetch_user(x["discord_id"]) for x in players_2]

        # Splitting logic
        for i in range(5):
            print(players_1[i])
            # await players_1[i].move_to(team_1)
            one_em.add_field(name=players_1[i].name, value=f"<@{players_2[i].id}>")
            print(players_2[i])
            # await players_2[i].move_to(team_2)
            two_em.add_field(name=players_2[i].name, value=f"<@{players_2[i].id}>")
       
       
        # Sending embeds and cleanup
        await self.send(embed=one_em)
        await self.send(embed=two_em)
        return 
    
    

        