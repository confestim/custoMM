from rest_framework import serializers

from .models import Player

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ('discord', 'lol', 'lol_id', 'discord_id', 'mmr')