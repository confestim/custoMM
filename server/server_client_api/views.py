from rest_framework import viewsets

from .serializers import PlayerSerializer
from .models import Player


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all().order_by('mmr')
    serializer_class = PlayerSerializer