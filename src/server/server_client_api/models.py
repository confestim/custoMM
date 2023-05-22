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

class Stats(models.Model):
    """LoL stats for each Player"""
    
    # Roles
    JUNGLE = "JGL"
    TOP = "TOP"
    MID = "MID"
    ADC = "ADC"
    SUPPORT = "SUP"
    FILL = "FILL"

    ROLE_CHOICES = [
        (JUNGLE, "Jungle"),
        (TOP, "Top"),
        (MID, "Middle"),
        (ADC, "Carry"),
        (SUPPORT, "Support"),
        (FILL, "Fill")
    ]
    
    # Player, associated with Player model
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    # Average KDA, Gold earned, Kill participation
    kda = models.FloatField(default=0)
    gold = models.FloatField(default=0)
    kp = models.FloatField(default=0)
    games_played = models.IntegerField(default=0)
    roles = models.JSONField(default=dict)
    usual_role = models.CharField(max_length=30, default=FILL, choices=ROLE_CHOICES)
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

    def __str__(self):
        return str(self.lobby_name)