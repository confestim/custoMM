from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'players', views.PlayerViewSet)
router.register(r'current', views.CurrentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('games/', views.games),
    path('game/', views.game),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
