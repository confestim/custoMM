from rest_framework import serializers

from .models import Player, Game, Current, Instructions


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ('discord', 'lol', 'lol_id', 'discord_id', 'mmr', 'usual_role', 'roles')

    def update(self, instance, validated_data):
        instance.discord_id = validated_data.get(
            'discord_id', instance.discord_id)
        instance.discord = validated_data.get('discord', instance.discord)
        instance.lol = validated_data.get('lol', instance.lol)
        instance.lol_id = validated_data.get('lol_id', instance.lol_id)
        instance.save()
        return instance


class InstructionsSerializer(serializers.ModelSerializer):
    
        class Meta:
            model = Instructions
            fields = ("game_id", "instructions")

class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = ("game_id",)

class CurrentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Current
        fields = ("lobby_name", "creator", "players", "teams", "bravery")

    def create(self, validated_data):
        """
        Create and return a new `Current` instance, given the validated data.
        """
        return Current.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.players = validated_data.get('players', instance.players)
        instance.lobby_name = validated_data.get('lobby_name', instance.lobby_name)
        instance.save()
        return instance