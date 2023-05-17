import asyncio
import discord
from discord.ext import commands
import requests
from urllib.parse import quote
from classes.Target import Target
import json 
import random 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    game = discord.Game("Custom Matchmaking - !help")
    await bot.change_presence(activity=game, status=discord.Status.dnd)
    

@bot.command(aliases=['random'])
async def randomize(ctx):
    """Randomizes 10 people into 2 teams: !randomize"""
    target = Target(ctx, bot)
    await target.randomize()
    return


@bot.command(aliases=['begin_game', 'game'])
async def ladder(ctx):
    """Tries to start a fair game: !ladder"""
    target = Target(ctx, bot)

    players = await target.ready()
    if not players:
        return
    
    valid_players = []
    
    # This does not support multiple accounts, refer to issue #7
    # Initial check for existing players
    for i in players:

        player = requests.get(f"{target.URL}/players/?search={i.id}").json()
        if not player:
            await ctx.send(f"<@{i.id}> has no league account associated with their name. Please register in order to calculate MMR more accurately.")
        else:
            valid_players.append(player[0]["lol"])

    # If not enough players, return
    if len(valid_players) < 10:
        return await ctx.send("Couldn't create fair game. Whoever isn't registered, please do.")

    # Getting the players
    query_string = "?"+"&".join(["players={}".format(quote(player)) for player in valid_players])
    print(query_string)
    teams = requests.get(
        f"{target.URL}/game/?{query_string}")

    # Second check for existing players
    # Also, funny status code
    if teams.status_code == 451:
        for i in teams.content:
            await ctx.send(f"{i} has not been found by the API. Please register in order to calculate MMR more accurately.")
        return
    
    teams = teams.json()
    # TODO: Debug, remove
    print(teams)
    
    await target.split(teams[0], teams[1], fair=True)

    # Create current game
    requests.post(f"{target.URL}/current/", data={
        "lobby_name": None,
        "players": 0,
        "creator": random.choice(valid_players),
        "teams": json.dumps(teams)
    })


    return


@bot.command(aliases=['r', 'reg'])
async def register(ctx, *args):
    """Registers a user to the database: !register <league_name>"""
    target = Target(ctx, bot)
    name = " ".join(args)

    if (len(name) < 4) or (requests.get(f"https://lolprofile.net/summoner/eune/{name}").status_code != 200):
        return await ctx.send("Provide a normal username (cAsE sEnSiTiVe)")
    print(target.URL)
    league_name = requests.get(f"{target.URL}/players/{name}").json()
    print(league_name)

    try:
        if not league_name["detail"] == "Not found.":
            return await ctx.send("Someone already claimed this account")
    except KeyError:
        if league_name["discord_id"]:
            return await ctx.send(f"{league_name['discord']} has claimed this account.")

    claim_account = requests.post(f"{target.URL}/players/", data={
        "discord": ctx.author.name,
        "discord_id": ctx.author.id,
        "lol": name
    })

    if not claim_account.json().get('discord_id') and claim_account.json().get("lol"):

        # In case that account doesn't exist at all
        claim_account = requests.put(f"{target.URL}/players/{name}/", data={
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

@bot.command(aliases=['lead', 'l'])
async def leaderboard(ctx, players="5"):
    """Shows the Top <players> leaderboard: !leaderboard <number_of_players/max>"""
    target = Target(ctx, bot)
    leaderboard = requests.get(f"{target.URL}/players").json()
    if len(leaderboard) < players:
        return await ctx.send(f"We don't have that many players in the database. We have {len(leaderboard)}.")
    if players == "MAX" or players == "max":
        players = len(leaderboard)
    #NASTY
    players = int(players)
    leaderboard = leaderboard[:players]
    embed = discord.Embed(title=f"Top {players} players", description="Ordered by mmr", color=0xFF5733)
    embed.set_author(name="custoMM", icon_url="https://git.confest.im/boyan_k/custoMM/raw/branch/main/images/smol_logo.png")
    fields = [embed.add_field(name=x['lol'], value=x['mmr']) for x in leaderboard]
    return await ctx.send(embed=embed)
    

# Change to your bot token in config.ini
bot.run(Target("no", bot).token)
