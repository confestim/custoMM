from django.db import models

class Player(models.Model):
    discord = models.CharField(max_length=60, unique=True, null=True)
    lol = models.CharField(primary_key=True, max_length=60, unique=True )
    lol_id = models.CharField(max_length=60, null=True, blank=True , unique=True)
    discord_id = models.IntegerField(null=True, blank=True)
    mmr = models.IntegerField(default=600, editable=False)
    games_played = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.discord}:{self.lol}"

class Game(models.Model):
    game_id = models.CharField(max_length=30, unique=True)


