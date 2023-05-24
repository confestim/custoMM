from discord.ext import commands
from discord import app_commands, Interaction
from classes.Config import Config
import requests
import discord

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['lead', 'l'])
    async def leaderboard(self, ctx, players=5):
          """Shows the Top <players> leaderboard: !leaderboard <number_of_players> <max>"""
          config = Config()
          leaderboard = requests.get(f"{config.URL}/players").json()
      
          if len(leaderboard) < players:
              return await ctx.send(f"We don't have that many players in the database. We have {len(leaderboard)}.")

          leaderboard = leaderboard[:players]
          embed = discord.Embed(title=f"Top {players} players", description="Ordered by mmr", color=0xFF5733)
          embed.set_author(name="custoMM", icon_url="https://git.confest.im/boyan_k/custoMM/raw/branch/main/images/smol_logo.png")
          fields = [embed.add_field(name=x['lol'], value=x['mmr']) for x in leaderboard]
          return await ctx.send(embed=embed)

    @app_commands.command(name="leaderboard", description="Shows the Top <players> leaderboard")
    async def leaderboard_slash(self, interaction: Interaction, players: int):
        """Shows the Top <players> leaderboard: !leaderboard <number_of_players> <max>"""
        config = Config()
        leaderboard = requests.get(f"{config.URL}/players").json()
    
        if len(leaderboard) < players:
            return await interaction.response.send_message(f"We don't have that many players in the database. We have {len(leaderboard)}.")

        leaderboard = leaderboard[:players]
        embed = discord.Embed(title=f"Top {players} players", description="Ordered by mmr", color=0xFF5733)
        embed.set_author(name="custoMM", icon_url="https://git.confest.im/boyan_k/custoMM/raw/branch/main/images/smol_logo.png")
        fields = [embed.add_field(name=x['lol'], value=x['mmr']) for x in leaderboard]
        return await interaction.response.send_message(embed=embed)
  
       
async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
