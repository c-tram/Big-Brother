from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'player-analytics', views.PlayerAnalyticsViewSet, basename='player-analytics')
router.register(r'pitcher-analytics', views.PitcherAnalyticsViewSet, basename='pitcher-analytics')
router.register(r'game-analytics', views.GameAnalyticsViewSet, basename='game-analytics')
router.register(r'advanced-team-stats', views.AdvancedTeamStatsViewSet, basename='advanced-team-stats')
router.register(r'team-matchups', views.TeamMatchupViewSet, basename='team-matchups')
router.register(r'season-trends', views.SeasonTrendViewSet, basename='season-trends')

urlpatterns = [
    path('', include(router.urls)),
]