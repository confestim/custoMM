import asyncio
import discord
from discord.ext import commands
import random
import requests

URL = "http://23.88.44.133:8000/players"
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    game = discord.Game("Customki - !randomize")
    await bot.change_presence(activity=game, status=discord.Status.dnd)

@bot.command()
# Simple randomizer
async def randomize(ctx):
    # Change these to designated team voice channels
    team_1 = bot.get_channel(1054534012963659826)
    team_2 = bot.get_channel(1054534093641089084)
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
        two_em.add_field(name=players[len(players) - (i + 1)].name, value=players[len(players) - (i + 1)].id)

    await ctx.send(embed=one_em)
    await ctx.send(embed=two_em)
    await trying_prompt.delete()
    return
    
@bot.command
async def begin_game(ctx):
    # Change these to designated team voice channels
    team_1 = bot.get_channel(1054534012963659826)
    team_2 = bot.get_channel(1054534093641089084)
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
    for i in players:
        player = request.get(URL + f"?search={i.id}").json
        if not player:
            await ctx.send(f"{i.name} has no league account associated with their name. Please register in order to calculate MMR more accurately.")
        else:
            valid_players.append(player["lol"])
    
    if valid_players < 10:
        await return ctx.send("Couldn't create fair game. Whoever isn't registered, please do.")
   
    teams = requests.get(URL + "/game", params = {"players": valid_players}).json()
    # Embedding
    one_em = discord.Embed(title=f"Team 1", colour=discord.Colour(0x8c0303))

    two_em = discord.Embed(title=f"Team 2", colour=discord.Colour(0x0B5394))
    for i in teams[0]:
        player = await bot.get_user(i["discord_id"])
        await player.move_to(team_1)
        one_em.add_field(name=player.name, value=i["lol"])
    for i in teams[1]:
        player = await bot.get_user(i["discord_id"])
        await player.move_to(team_2)
        two_em.add_field(name=player.name, value=i["lol"])
   
    await ctx.send(embed=one_em)
    await ctx.send(embed=two_em)
    await trying_prompt.delete()
    return
@bot.command()
async def register(ctx, *args):

    name = " ".join(args)
    print(name)
    league_name = requests.get(URL + f"/{name}").json()
    print(league_name)
    if league_name:
        return await ctx.send("Someone already claimed this account")
     
   
    claim_account = requests.post(URL + "/", data = {
        "discord": ctx.author.name,
        "discord_id": ctx.author.id,
        "lol": name
    }
    )
    if claim_account.status_code == 201:
        return await ctx.send("Success, now approve from client")
    return await ctx.send("Something went wrong...")
    
# Change to your bot token
bot.run('TOKEN')


