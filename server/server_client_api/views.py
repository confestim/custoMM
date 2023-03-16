from rest_framework import viewsets, filters
from .serializers import PlayerSerializer
from .models import Player


class PlayerViewSet(viewsets.ModelViewSet):
    search_fields = ['discord','lol']
    filter_backends = (filters.SearchFilter,)
    queryset = Player.objects.all().order_by('mmr')
    serializer_class = PlayerSerializer