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

class Instructions(models.Model):
    game_id = models.CharField(max_length=30, unique=True)
    instructions = models.JSONField(default=dict)

class Stats(models.Model):
    """LoL stats for each Player"""
    
    # TODO: Implement in views, serializers and client


    
    # Player, associated with Player model
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    # Average KDA, Gold earned, Kill participation
    kda = models.FloatField(default=0)
    gold = models.FloatField(default=0)
    kp = models.FloatField(default=0)
    games_played = models.IntegerField(default=0)
    roles = models.JSONField(default=dict)
    # {"TOP":0, "JUNGLE":0, "MIDDLE":0, "ADC":0, "SUPPORT":0, "OTHER":0}
    usual_role = models.CharField(max_length=30, default="FILL")
    def __str__(self):
        return f"{self.player} - KDA:{self.kda}, Gold:{self.gold}, KP:{self.kp}"

class Game(models.Model):
    game_id = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return str(self.game_id)

class Current(models.Model):
    lobby_name = models.CharField(max_length=30, unique=True)
    players = models.IntegerField(default=0)
    creator = models.CharField(max_length=30, unique=True, primary_key=True,)
    teams = models.JSONField(default=dict)
    bravery = models.JSONField()

    def __str__(self):
        return str(self.lobby_name)