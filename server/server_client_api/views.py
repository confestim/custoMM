from rest_framework import viewsets, filters, mixins
from rest_framework.response import Response
from .serializers import PlayerSerializer, GameSerializer
from .models import Player, Game
import random

import math
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

class WhatTheFuckDidYouDo(Exception):
    # We raise this when we don't know what the fuck happened
    def __init__(self, message="Congrats, you broke this program, please explain your steps as an issue at https://github.com/confestim/custoMM"):
        self.message = message
        super().__init__(self.message)

class PlayerViewSet(viewsets.ModelViewSet):
    search_fields = ['discord','lol']
    filter_backends = (filters.SearchFilter,)
    queryset = Player.objects.all().order_by('mmr')
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


@api_view(['GET', 'POST'])
def games(request):
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
       


def mmr_on_game(ign:str, avg_enemy_mmr:int, kda:float, outcome:bool):
    
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
        raise WhatTheFuckDidYouDo()
        
    # Save to player
    player.mmr = mmr_change
    player.games_played += 1
    player.save()

    # TODO REMOVE DEBUG
    return print(f"Recalculated {ign}'s MMR to {mmr_change}") 


# Example game


def average_mmr(game):
    teams = game["participants"]
    outcome = ("t1","t2") if teams["t1"]["won"] else ("t2","t1")
    
    winners = list()
    losers = list()
    player_count = 1
    
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
    

def parse_game(game):
    teams = game["participants"]
    winner, loser = average_mmr(game)
    
    average = winner if teams["t1"]["won"] else loser 
    win_loss = True if teams["t1"]["won"] else False
    # ign:str, avg_enemy_mmr:int, kda:float, outcome:bool
        
    # get rid of the 2 loops, merge them into one
    for player in teams["t1"]["summoners"]:
        print(player)
        mmr_on_game(player["name"], average, player["kda"], win_loss)
    
    
    win_loss = not win_loss
    average = winner if win_loss else loser
    
    for player in teams["t2"]["summoners"]:
        print(player)
        mmr_on_game(player["name"], average, player["kda"], win_loss)
    
    return print("Done with changing mmr") 
    


