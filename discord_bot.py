import asyncio
import discord
from discord.ext import commands
import random
import requests
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
URL = config["DEFAULT"]["URL"]


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    game = discord.Game("Customki - !randomize")
    await bot.change_presence(activity=game, status=discord.Status.dnd)


@bot.command()
async def randomize(ctx,
                    team_1 = config['DISCORD']['TEAM_1'],
                    team_2 = config['DISCORD']['TEAM_2']):
    """Randomizes 10 people into 2 teams: !randomize"""

    # Change these to designated team voice channels in config.ini
    team_1 = bot.get_channel(team_1)
    team_2 = bot.get_channel(team_2)
    trying_prompt = await ctx.send('Trying to randomize!')

    # Fetching user channel
    try:
        channel = bot.get_channel(ctx.author.voice.channel.id)
    except AttributeError:
        await trying_prompt.delete()
        return await ctx.send("You think you're cool or something? Get in a channel first.")

    players = channel.members
    if len(players) < 10:
        await trying_prompt.delete()
        await ctx.send(f"Get more people in ({len(players)}/10)")
        return
    random.shuffle(players)
    print(players)

    # Embedding
    one_em = discord.Embed(title=f"Team 1", colour=discord.Colour(0x8c0303))

    two_em = discord.Embed(title=f"Team 2", colour=discord.Colour(0x0B5394))
    # Splitting logic
    modulus = len(players) % 10
    if modulus != 0:
        # If total players not divisible by 10, can't split
        return await ctx.send("Can't split(remove bots and non-players)")

    # Else, start at bottom and at top and move to middle
    for i in range(0, int(len(players)/2)):
        await players[i].move_to(team_1)
        one_em.add_field(name=players[i].name, value=players[i].id)
        await players[len(players) - (i + 1)].move_to(team_2)
        two_em.add_field(name=players[len(
            players) - (i + 1)].name, value=players[len(players) - (i + 1)].id)

    await ctx.send(embed=one_em)
    await ctx.send(embed=two_em)
    await trying_prompt.delete()
    return


@bot.command()
async def begin_game(ctx,
                     team_1 = config['DISCORD']['TEAM_1'],
                     team_2 = config['DISCORD']['TEAM_2']):
    """Tries to start a fair game: !begin_game"""
    # Change these to designated team voice channels
    team_1 = bot.get_channel(team_1)
    team_2 = bot.get_channel(team_2)

    trying_prompt = await ctx.send('Trying to start fair game!')

    # Fetching user channel
    try:
        channel = bot.get_channel(ctx.author.voice.channel.id)
    except AttributeError:
        await trying_prompt.delete()
        return await ctx.send("You think you're cool or something? Get in a channel first.")

    players = channel.members
    if len(players) < 10:
        await trying_prompt.delete()
        await ctx.send(f"Get more people in ({len(players)}/10)")
        return

    valid_players = []
    # This does not support multiple accounts, refer to issue #7
    # Initial check for existing players
    for i in players:
        print(i.name)
        player = requests.get(f"{URL}/players/?search={i.id}").json()
        print(player)
        if not player:
            await ctx.send(f"<@{i.id}> has no league account associated with their name. Please register in order to calculate MMR more accurately.")
        else:
            valid_players.append(player[0]["lol"])

    # If not enough players, return
    if len(valid_players) < 10:
        return await ctx.send("Couldn't create fair game. Whoever isn't registered, please do.")

    # Getting the players
    query_string = "&".join(["".format(player) for player in valid_players])

    teams = requests.get(
        f"{URL}/game?{query_string}")

    # Second check for existing players
    # Also, funny status code
    if teams.status_code == 451:
        for i in teams.content:
            await ctx.send(f"{i} has not been found by the API. Please register in order to calculate MMR more accurately.")
        return
    teams = teams.json()
    # Embedding
    one_em = discord.Embed(title=f"Team 1", colour=discord.Colour(0x8c0303))

    two_em = discord.Embed(title=f"Team 2", colour=discord.Colour(0x0B5394))
    
    # TODO: DEBUG, remove
    print(teams)

    # Splitting logic
    for i in teams[0]:
        player = await bot.get_user(i["discord_id"])
        await player.move_to(team_1)
        one_em.add_field(name=player.name, value=i["lol"])
    for i in teams[1]:
        player = await bot.get_user(i["discord_id"])
        await player.move_to(team_2)
        two_em.add_field(name=player.name, value=i["lol"])

    # Sending embeds and cleanup
    await ctx.send(embed=one_em)
    await ctx.send(embed=two_em)
    await trying_prompt.delete()
    return


@bot.command()
async def register(ctx, *args):
    """Registers a user to the database: !register <league_name>"""
    name = " ".join(args)
    print(name)
    league_name = requests.get(f"{URL}/players/{name}").json()
    print(league_name)

    try:
        if not league_name["detail"] == "Not found.":
            return await ctx.send("Someone already claimed this account")
    except KeyError:
        if league_name["discord_id"]:
            return await ctx.send(f"{league_name['discord']} has claimed this account.")

    claim_account = requests.post(f"{URL}/players/", data={
        "discord": ctx.author.name,
        "discord_id": ctx.author.id,
        "lol": name
    })

    if not claim_account.json().get('discord_id') and claim_account.json().get("lol"):

        # In case that account doesn't exist at all
        claim_account = requests.put(f"{URL}/players/{name}/", data={
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

# Change to your bot token in config.ini
bot.run(config['DISCORD']['TOKEN'])
