from discord.ext import commands
from discord import app_commands, Interaction
from classes.Config import Config
from classes.Leaderboard import Leaderboard
import requests
import discord

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !Command
    @commands.command(aliases=['lead', 'l'])
    async def leaderboard(self, ctx, players=5):
        """Shows the Top <players> leaderboard: !leaderboard <number_of_players> <max>"""
        lead = Leaderboard(bot=self.bot, author=ctx.author, ctx=ctx, players=players)
        await lead.leaderboard()
    # /Command
    @app_commands.command(name="leaderboard", description="Shows the Top <players> leaderboard")
    async def leaderboard_slash(self, interaction: Interaction, players: int=5):
        """Shows the Top <players> leaderboard: !leaderboard <number_of_players> <max>"""
        lead = Leaderboard(bot=self.bot, author = interaction.user, interaction=interaction, slash=True, players=players)
        await lead.leaderboard()
  
       
async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
