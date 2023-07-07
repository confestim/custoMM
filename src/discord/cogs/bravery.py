from discord.ext import commands
from discord import app_commands, Interaction
from classes.Fair import Fair


class BraveryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !Command
    @commands.command(aliases=['ultimate_bravery', 'ultimate'])
    async def bravery(self, ctx):
        fair = Fair(bot=self.bot, author=ctx.author, ctx=ctx,bravery=True)
        await fair.divide()

    # /Command
    @app_commands.command(name="Ultimate Bravery", description="Splits the teams fairly, but everyone is forced to play ultimate bravery.")
    async def bravery(self, interaction: Interaction):
        fair = Fair(bot=self.bot, author=interaction.user, interaction=interaction, slash=True,bravery=True)
        await fair.divide()

        
async def setup(bot):
    await bot.add_cog(BraveryCog(bot))