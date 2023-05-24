from discord.ext import commands
from classes.Randomizer import Randomizer
from discord import app_commands, Interaction

class RandomizeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['random'])
    async def randomize(self, ctx):
        """Randomizes 10 players into teams: !randomize"""
        randomizer = Randomizer(bot=self.bot, author = ctx.author, ctx=ctx)
        await randomizer.randomize()
        return

    @app_commands.command(name="randomize", description="Randomizes 10 players into teams")
    async def randomize_slash(self, interaction: Interaction):
        """Randomizes 10 players into teams: !randomize"""
        randomizer = Randomizer(bot=self.bot, author = interaction.user, interaction=interaction, slash=True)
        await randomizer.randomize()
        return
    
async def setup(bot):
    await bot.add_cog(RandomizeCog(bot))
