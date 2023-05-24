from discord.ext import commands
from classes.Config import Config
import requests
from discord import app_commands, Interaction

class RegisterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['r', 'reg'])
    async def register(self, ctx, *args):
        """Registers a user to the database: !register <league_name>"""
        config = Config()
        name = " ".join(args)

        if (len(name) < 4) or (requests.get(f"https://lolprofile.net/summoner/eune/{name}").status_code != 200):
            return await ctx.send("Provide a normal username (cAsE sEnSiTiVe)")
        league_name = requests.get(f"{config.URL}/players/{name}").json()

        try:
            if not league_name["detail"] == "Not found.":
                return await ctx.send("Someone already claimed this account")
        except KeyError:
            if league_name["discord_id"]:
                return await ctx.send(f"{league_name['discord']} has claimed this account.")

        claim_account = requests.post(f"{config.URL}/players/", data={
            "discord": ctx.author.name,
            "discord_id": ctx.author.id,
            "lol": name
        })

        if not claim_account.json().get('discord_id') and claim_account.json().get("lol"):

            # In case that account doesn't exist at all
            claim_account = requests.put(f"{config.URL}/players/{name}/", data={
                "discord": ctx.author.name,
                "discord_id": ctx.author.id,
                "lol": name
            })
            print(claim_account.content)

        # TODO: In case the account exists, but not yet claimed

        print(claim_account.status_code)
        if claim_account.status_code == 201 or claim_account.status_code == 200:
            return await ctx.send("Success, now approve from client")
        return await ctx.send("Something went wrong...")
    
    @app_commands.command(name="register", description="Creates a new account on server")
    async def registerSlash(self, interaction: Interaction, name: str):
        """Registers a user to the database: !register <league_name>"""
        config = Config()
        
        if (len(name) < 4) or (requests.get(f"https://lolprofile.net/summoner/eune/{name}").status_code != 200):
            return await interaction.response.send_message("Provide a normal username (cAsE sEnSiTiVe)")
        league_name = requests.get(f"{config.URL}/players/{name}").json()

        try:
            if not league_name["detail"] == "Not found.":
                return await interaction.response.send_message("Someone already claimed this account")
        except KeyError:
            if league_name["discord_id"]:
                return await interaction.response.send_message(f"{league_name['discord']} has claimed this account.")

        claim_account = requests.post(f"{config.URL}/players/", data={
          # In case that account doesn't exist at all

            "discord": interaction.user.name,
            "discord_id": interaction.user.id,
            "lol": name
        })

        if not claim_account.json().get('discord_id') and claim_account.json().get("lol"):
            # In case it exists but not claimed
            claim_account = requests.put(f"{config.URL}/players/{name}/", data={
                "discord": interaction.user.name,
                "discord_id": interaction.user.id,
                "lol": name
            })

        # TODO: In case the account exists, but not yet claimed

        print(claim_account.status_code)
        if claim_account.status_code == 201 or claim_account.status_code == 200:
            return await interaction.response.send_message("Success, now approve from client")
        return await interaction.response.send_message("Something went wrong...")
    

async def setup(bot):
    await bot.add_cog(RegisterCog(bot))
