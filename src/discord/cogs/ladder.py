from discord.ext import commands
from discord import app_commands, Interaction
from classes.Fair import Fair


class LadderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !Command
    @commands.command(aliases=['begin_game', 'game'])
    async def ladder(self, ctx):
        fair = Fair(bot=self.bot, author=ctx.author, ctx=ctx)
        await fair.divide()

    # /Command
    @app_commands.command(name="ladder", description="Tries to start a fair game")
    async def ladder(self, interaction: Interaction):
        fair = Fair(bot=self.bot, author=interaction.user, interaction=interaction, slash=True)
        await fair.divide()

        
async def setup(bot):
    await bot.add_cog(LadderCog(bot))
