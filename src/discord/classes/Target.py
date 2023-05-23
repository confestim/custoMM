import configparser
import discord
from discord.ext import commands
import asyncio
from typing import List
import random

class Target:
    def __init__(self, ctx, bot:commands.Bot):
      
        config = configparser.ConfigParser()
        config.read("../config.ini")
        self.URL = config["DEFAULT"]["URL"]
        self.team_1 = config['DISCORD']['TEAM_1']
        self.team_2 = config['DISCORD']['TEAM_2']
        self.token = config['DISCORD']['TOKEN']
        self.ctx = ctx
        self.bot = bot

    async def ready(self) -> bool:
        """
        Checks if players are ready to be split
        """
        self.trying_prompt = await self.ctx.send('Trying to start!')

        # Fetching user channel
        try:
            channel = self.bot.get_channel(self.ctx.author.voice.channel.id)
        except AttributeError:
            await self.trying_prompt.delete()
            await self.ctx.send("You think you're cool or something? Get in a channel first.")
            return False

        players = channel.members
        if len(players) < 10:
            await self.trying_prompt.delete()
            await self.ctx.send(f"Get more people in ({len(players)}/10)")
            return False

        if len(players) % 10 != 0:
        # If total players not divisible by 10, can't split
            await self.ctx.send("Can't split(remove bots and non-players)")
            return False
        
        return players     
      
    async def split(self, players_1, players_2, fair=False):
        """
        Splits players into 2 teams
        """
        await self.ctx.send(self.bot)
        # Declaring channels
        team_1 = await self.bot.get_channel(self.team_1)
        team_2 = await self.bot.get_channel(self.team_2)
        
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
            await players_1[i].move_to(team_1)
            one_em.add_field(name=players_1[i].name, value=f"<@{players_2[i].id}>")
            await players_2[i].move_to(team_2)
            two_em.add_field(name=players_2[i].name, value=f"<@{players_2[i].id}>")

        # Sending embeds and cleanup
        await self.ctx.send(embed=one_em)
        await self.ctx.send(embed=two_em)
        await self.trying_prompt.delete()
        return
    
    async def randomize(self):
        players = await self.ready()
        if not players:
            return False
        
        random.shuffle(players)

        await self.split(players[:int(len(players)/2)], players[int(len(players)/2):])
        return True
        
