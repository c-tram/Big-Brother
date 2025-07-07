from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'leagues', views.LeagueViewSet)
router.register(r'divisions', views.DivisionViewSet)
router.register(r'venues', views.VenueViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'team-seasons', views.TeamSeasonViewSet)
router.register(r'team-stats', views.TeamStatsViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('standings/', views.standings_view, name='standings'),
]