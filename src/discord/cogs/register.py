from discord.ext import commands
from classes.Register import Register
from discord import app_commands, Interaction

class RegisterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['r', 'reg'])
    async def register(self, ctx, *args):
        registration = Register(self.bot, ctx.author, ctx, slash=False, player=args)
        await registration.register()
    
    @app_commands.command(name="register", description="Creates a new account on server")
    async def registerSlash(self, interaction: Interaction, name: str):
        registration = Register(self.bot, interaction.author, interaction=interaction, slash=True, player=name)
        await registration.register()

async def setup(bot):
    await bot.add_cog(RegisterCog(bot))
