from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'players', views.PlayerViewSet)
router.register(r'team-history', views.PlayerTeamHistoryViewSet)
router.register(r'seasons', views.PlayerSeasonViewSet)
router.register(r'pitcher-seasons', views.PitcherSeasonViewSet)
router.register(r'awards', views.PlayerAwardViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]