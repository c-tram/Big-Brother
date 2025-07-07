from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'games', views.GameViewSet)
router.register(r'series', views.GameSeriesViewSet)
router.register(r'line-scores', views.GameLineScoreViewSet)
router.register(r'events', views.GameEventViewSet)
router.register(r'player-stats', views.GamePlayerStatsViewSet)
router.register(r'pitcher-stats', views.GamePitcherStatsViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]