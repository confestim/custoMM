from rest_framework import serializers

from .models import Player, Game

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ('discord', 'lol', 'lol_id', 'discord_id')

    def update(self, instance, validated_data):
        instance.discord = validated_data.get('discord', instance.discord)
        instance.lol = validated_data.get('lol', instance.lol)
        instance.lol_id = validated_data.get('lol_id', instance.lol_id)
        instance.save()
        return instance

class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ("game_id",)

