from rest_framework import viewsets, filters, mixins
from rest_framework.response import Response
from .serializers import PlayerSerializer, GameSerializer, CurrentSerializer, InstructionsSerializer
from .models import Player, Game, Current, Instructions

import math
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


class PlayerViewSet(viewsets.ModelViewSet):
    """
    Display and interaction with the players in the database
    """
    search_fields = ['discord_id','lol']
    filter_backends = (filters.SearchFilter,)
    queryset = Player.objects.all().order_by('mmr').reverse()
    serializer_class = PlayerSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        discord_id = kwargs.get('pk')
        instance = Player.objects.get(discord_id=discord_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CurrentViewSet(viewsets.ModelViewSet):
    """
    Display and interaction with the active games in the database
    """
    
    queryset = Current.objects.all()
    serializer_class = CurrentSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = Current.objects.get(creator=request.data.get("creator"))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def instructions(request):
    # TODO: Implement
    """
    Instructions for every player during the game.
    This a troll function, it should be disabled in the client if you don't want it.
    """

    possible_instructions = [
        "troll", # (everybody flashes at the same time)
        "emote", # (everybody spams emotes)
        "skin", # (everybody writes their skin)
        "summoner", # (everybody writes their summoner name)
        "dance", # (everybody dances)
        "laugh", # (everybody laughs)
        "joke", # (everybody tells a joke)
        "taunt", # (everybody taunts)
        "recall", # (everybody recalls)
        ]
    if request.method == 'GET':
        instructions = Instructions.objects.all()
        serializer = InstructionsSerializer(instructions, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        if request.data.get("game_id") is None:
            return Response("No game id provided.", status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("instructions") is None or request.data.get("user") is None:
            return Response("No instructions provided.", status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("instructions") not in possible_instructions or request.data.get("user") not in Player.objects.all():
            return Response("Invalid instruction.", status=status.HTTP_400_BAD_REQUEST)
        instructions, created = Instructions.objects.get_or_create(game_id=request.data.get("game_id"))
        if not created:
            # Add to json field
            instructions.instructions[request.data.get("user")].append(request.data.get("instructions"))
            instructions.save()
            return Response("Added.", status=status.HTTP_201_CREATED)
        else:
            # Create json field
            instructions.instructions = {request.data.get("user"): [request.data.get("instructions")]}
            instructions.save()
            return Response("Added.", status=status.HTTP_201_CREATED)
        

@api_view(['GET', 'POST'])
def games(request):
    """
    Interaction with logging games.
    Returns codes of games that have already been looked at 
    and accepts new games. No checks are being done in this function itself, all checks are within the client.
    """
    if request.method == 'GET':
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        
            print(request.data["game_id"])
            game, created = Game.objects.get_or_create(game_id=int(request.data.get("game_id")))
            if not created:
                return Response("Game already exists.", status=status.HTTP_409_CONFLICT)
            parse_game(request.data)
            return Response("Added.", status=status.HTTP_201_CREATED)

@api_view(['GET'])
def game(request):
    """
    Returns fair team composition for a given list of players
    """
    player_ids = request.GET.getlist("players")
    players = list()
    failed = False
    for player in player_ids:
        # This doesn't support multiple accounts for each user, refer to issue #8
        try:
            p = Player.objects.get(lol=player)
            players.append({"lol": p.lol, "discord_id":p.discord_id, "mmr":p.mmr, "status": True})
        except Player.DoesNotExist:
            failed = True
            players.append({"lol": player, "found": False})

    if failed:
        return Response([x for x in players if x["found"] == False], status=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)
    


    # Sort the list of players based on their mmr values
    players.sort(key=lambda x: x['mmr'], reverse=True)

    # Initialize the two groups as empty lists
    group1 = []
    group2 = []

    # Add players to each group, alternating between the two groups
    for i, player in enumerate(players):
        if i % 2 == 0:
            group1.append(player)
        else:
            group2.append(player)

    # Calculate the total mmr of each group
    group1_total = sum(player['mmr'] for player in group1)
    group2_total = sum(player['mmr'] for player in group2)

    # While the difference between the total mmr of the two groups is greater than 100, move a player from the group with the higher total mmr to the group with the lower total mmr
    while abs(group1_total - group2_total) > 200:
        if group1_total > group2_total:
            # Remove a player from group 1 and add them to group 2
            player = group1.pop(0)
            group2.append(player)

            # Update the total mmr of each group
            group1_total -= player['mmr']
            group2_total += player['mmr']
        else:
            # Remove a player from group 2 and add them to group 1
            player = group2.pop(0)
            group1.append(player)

            # Update the total mmr of each group
            group2_total -= player['mmr']
            group1_total += player['mmr']

    # Create two teams of five players each
    team1 = group1[::2] + group2[1::2]
    team2 = group2[::2] + group1[1::2]
    
    return Response((team1, team2), status=status.HTTP_200_OK)



def mmr_on_game(ign:str, avg_enemy_mmr:int, kda:float, outcome:bool):
    """
    MMR changing function
    ELO rating system implementation
    """
    # Calculate probability of win
    # 1 / (1 + ((loser-winner)^10)/400)
    player = Player.objects.get(lol=ign)
    mmr_change = player.mmr
    expected_probability = 1 / (1 + math.pow(10, avg_enemy_mmr - mmr_change)/400)
    
    multiplier = 24
    # Increase multiplier if player is new
    if player.games_played < 10:
        multiplier = 32
    
    # Calculate mmr if win
    if outcome: 
        mmr_change = mmr_change + kda * (1-expected_probability) + multiplier*(1-expected_probability)
    
    # If loss
    elif not outcome:
        # Mitigate some of the loss if kda is high 
        mmr_change = mmr_change - multiplier*(1-expected_probability) + kda*(1-expected_probability)
    
    # I feel like this could bug out(magically), so raise exception if neither of these is the case
    else:
        raise Exception()
        
    # Save to player
    player.mmr = mmr_change
    player.games_played += 1
    player.save()

    # TODO REMOVE DEBUG
    return print(f"Recalculated {ign}'s MMR to {mmr_change}") 


# Example game


def average_mmr(game):
    """
    Average MMR function
    Calculates average mmr for a given game
    """
    teams = game["participants"]
    outcome = ("t1","t2") if teams["t1"]["won"] else ("t2","t1")
    
    winners = list()
    losers = list()
    player_count = 1
    
    # Gets average for each the losers and the winners
    for team in outcome:
        for user in teams[team]["summoners"]:
            print(user["name"])
            try:
                player = Player.objects.get(lol=user["name"])
            except Player.DoesNotExist:
                player = Player.objects.create(lol=user["name"])
                print(f"{player.lol} has just been created.")
           
            if len(winners) <= 5:
                winners.append(player.mmr)
            
            else:
                losers.append(player.mmr)

            player_count += 1

    return sum(winners)/5, sum(losers)/5
    
def update_roles(gamer, role, lane):
    try:
        player = Player.objects.get(lol=gamer)
    except Player.DoesNotExist:
        player = Player.objects.create(lol=gamer)

    if lane == "TOP":
        player.roles["TOP"] += 1
    elif lane == "JUNGLE":
        player.roles["JUNGLE"] += 1
    elif lane == "MIDDLE":
        player.roles["MIDDLE"] += 1
    elif lane == "BOTTOM" and role == "CARRY":
        player.roles["ADC"] += 1
    elif lane == "BOTTOM" and role == "SUPPORT":
        player.roles["SUPPORT"]
    else:
        player.roles["OTHER"] += 1

    most_played = max(player.roles, key=lambda x: player.roles[x])
    if most_played != player.usual_role:
        player.usual_role = most_played
        
    player.save()
    
def parse_game(game):
    """
    Parse game function
    Calculates mmr for each player in a given game
    Changes their mmr accordingly
    """
    teams = game["participants"]
    winner, loser = average_mmr(game)
    
    average = winner if teams["t1"]["won"] else loser 
    win_loss = True if teams["t1"]["won"] else False
    # ign:str, avg_enemy_mmr:int, kda:float, outcome:bool
        
    # get rid of the 2 loops, merge them into one
    for player in teams["t1"]["summoners"]:
        print(player)
        mmr_on_game(player["name"], average, player["kda"], win_loss)
        update_roles(player["name"], player["role"],player["lane"])
    
    
    win_loss = not win_loss
    average = winner if win_loss else loser
    
    for player in teams["t2"]["summoners"]:
        print(player)
        mmr_on_game(player["name"], average, player["kda"], win_loss)
        update_roles(player["name"], player["role"], player["lane"])

    return print("Done with changing mmr") 
    


