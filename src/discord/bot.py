import asyncio
import discord
from discord.ext import commands
from classes.Splitter import Splitter
from classes.Config import Config
from os import listdir
intents = discord.Intents.all()


config = Config()

class custoMM(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def load_extensions(self):
        for filename in listdir("./cogs"):
            if filename.endswith(".py"):
                # cut off the .py from the file name
                await bot.load_extension(f"cogs.{filename[:-3]}")

    async def setup_hook(self):
        await self.load_extensions()
        bot.tree.clear_commands(guild=discord.Object(id=config.guild))
        await self.tree.sync(guild=discord.Object(id=config.guild)) 

    async def on_ready(self):
        synced = await self.tree.sync()
        print("-------------------")
        print("Synced " +  str(len(synced)) + " commands")
        [print(f"Synced {x.name}") for x in synced]
        print("-------------------")
        print(f'Logged in as {bot.user}')
        game = discord.Game("Custom Matchmaking - !help")
        await bot.change_presence(activity=game, status=discord.Status.dnd)
        print("Displaying status as " + str(game))
        print("-------------------")
    # Load the cogs

bot = custoMM()

# Change to your bot token in config.ini
bot.run(config.token,reconnect=True)
