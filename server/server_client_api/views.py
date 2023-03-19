from rest_framework import viewsets, filters
from rest_framework.response import Response
from .serializers import PlayerSerializer
from .models import Player


class PlayerViewSet(viewsets.ModelViewSet):
    search_fields = ['discord','lol']
    filter_backends = (filters.SearchFilter,)
    queryset = Player.objects.all().order_by('mmr')
    serializer_class = PlayerSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    def delete(self, request, *args, **kwargs):
        discord_id = kwargs.get('pk')
        instance = Player.objects.get(discord_id=discord_id)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
