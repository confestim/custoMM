from django.db import models

class Player(models.Model):
    discord = models.CharField(max_length=60, unique=True, null=True)
    lol = models.CharField(primary_key=True, max_length=60, unique=True )
    lol_id = models.CharField(max_length=60, null=True, blank=True , unique=True)
    discord_id = models.IntegerField(null=True, blank=True)
    mmr = models.IntegerField(default=600, editable=False)
    #mmr = models.IntegerField(default=600)
    games_played = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.discord}:{self.lol}"

class Game(models.Model):
    game_id = models.CharField(max_length=30, unique=True)


class Current(models.Model):
    lobby_name = models.CharField(max_length=30, unique=True)
    players = models.IntegerField(default=0)
    creator = models.CharField(max_length=30, unique=True)
    teams = models.JSONField(default=dict)

    def __str__(self):
        return str(self.lobby_name)