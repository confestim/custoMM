from django.db import models

class Player(models.Model):
    discord = models.CharField(max_length=60)
    lol = models.CharField(max_length=60)
    lol_id = models.CharField(max_length=60)
    discord_id = models.IntegerField(primary_key=True)
    mmr = models.IntegerField()
    def __str__(self):
        return f"{self.discord}:{self.lol}"