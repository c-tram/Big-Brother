from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Q
from .models import League, Division, Venue, Team, TeamSeason, TeamStats
from .serializers import (
    LeagueSerializer, DivisionSerializer, VenueSerializer, 
    TeamSerializer, TeamDetailSerializer, TeamSeasonSerializer, TeamStatsSerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])
def standings_view(request):
    """
    Get current MLB standings organized by league and division
    """
    try:
        season = request.query_params.get('season', 2025)  # Default to current season
        
        # Get team seasons for the specified season
        team_seasons = TeamSeason.objects.filter(
            season=season
        ).select_related(
            'team', 'team__league', 'team__division'
        ).order_by(
            'team__league__name', 
            'team__division__name', 
            '-win_percentage',
            '-wins'
        )
        
        standings = {
            'AL': {
                'East': [],
                'Central': [],
                'West': []
            },
            'NL': {
                'East': [],
                'Central': [],
                'West': []
            }
        }
        
        for team_season in team_seasons:
            team = team_season.team
            league = team.league.abbreviation if team.league else 'AL'
            division = team.division.name.split()[-1] if team.division else 'East'  # Get last word (East/Central/West)
            
            team_data = {
                'id': team.id,
                'name': team.name,
                'abbreviation': team.abbreviation,
                'wins': team_season.wins,
                'losses': team_season.losses,
                'winning_percentage': float(team_season.win_percentage) if team_season.win_percentage else 0.0,
                'games_back': team_season.games_back if hasattr(team_season, 'games_back') else 0,
                'streak': f"{team_season.streak_type}{team_season.streak_number}" if hasattr(team_season, 'streak_type') and hasattr(team_season, 'streak_number') else 'N/A',
                'last_10': getattr(team_season, 'last_10', 'N/A')
            }
            
            if league in standings and division in standings[league]:
                standings[league][division].append(team_data)
        
        # Calculate games back for each division
        for league in standings:
            for division in standings[league]:
                if standings[league][division]:
                    # First place team has 0 games back
                    first_place_wins = standings[league][division][0]['wins']
                    first_place_losses = standings[league][division][0]['losses']
                    
                    for i, team in enumerate(standings[league][division]):
                        if i == 0:
                            team['games_back'] = 0.0
                        else:
                            # Games back = ((First place wins - team wins) + (team losses - first place losses)) / 2
                            games_back = ((first_place_wins - team['wins']) + (team['losses'] - first_place_losses)) / 2
                            team['games_back'] = round(games_back, 1)
        
        return Response(standings, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get standings: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MLB Leagues (AL/NL)"""
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['abbreviation', 'name']
    search_fields = ['name', 'abbreviation']
    ordering_fields = ['name', 'abbreviation']
    ordering = ['name']

class DivisionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MLB Divisions"""
    queryset = Division.objects.select_related('league').all()
    serializer_class = DivisionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['league__abbreviation', 'abbreviation', 'name']
    search_fields = ['name', 'abbreviation', 'league__name']
    ordering_fields = ['name', 'abbreviation', 'league__name']
    ordering = ['league__name', 'name']

class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MLB Venues/Stadiums"""
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['city', 'state', 'country', 'surface', 'roof_type']
    search_fields = ['name', 'city', 'state']
    ordering_fields = ['name', 'city', 'capacity']
    ordering = ['name']

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MLB Teams"""
    queryset = Team.objects.select_related('league', 'division', 'venue').all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['league__abbreviation', 'division__abbreviation', 'active']
    search_fields = ['name', 'team_name', 'abbreviation', 'venue__city']
    ordering_fields = ['name', 'team_name', 'abbreviation', 'venue__city']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamDetailSerializer
        return TeamSerializer

    @action(detail=True, methods=['get'])
    def seasons(self, request, pk=None):
        """Get all seasons for a team"""
        team = self.get_object()
        seasons = TeamSeason.objects.filter(team=team).order_by('-season')
        serializer = TeamSeasonSerializer(seasons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get stats for a team"""
        team = self.get_object()
        season = request.query_params.get('season')
        
        stats_queryset = TeamStats.objects.filter(team_season__team=team)
        if season:
            stats_queryset = stats_queryset.filter(team_season__season=season)
        
        stats = stats_queryset.order_by('-team_season__season')
        serializer = TeamStatsSerializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get complete team profile with stats"""
        team = self.get_object()
        season = request.query_params.get('season', 2024)
        
        # Get latest season data
        latest_season = TeamSeason.objects.filter(team=team).order_by('-season').first()
        
        # Get latest stats
        latest_stats = TeamStats.objects.filter(team_season__team=team).order_by('-team_season__season').first()
        
        profile_data = {
            'id': team.id,
            'name': team.name,
            'team_name': team.team_name,
            'location_name': team.location_name,
            'abbreviation': team.abbreviation,
            'league': team.league.name if team.league else None,
            'division': team.division.name if team.division else None,
            'venue': {
                'name': team.venue.name if team.venue else None,
                'city': team.venue.city if team.venue else None,
                'capacity': team.venue.capacity if team.venue else None,
            } if team.venue else None,
            'season_record': {
                'wins': latest_season.wins if latest_season else 0,
                'losses': latest_season.losses if latest_season else 0,
                'win_percentage': float(latest_season.win_percentage) if latest_season and latest_season.win_percentage else 0.0,
                'games_played': latest_season.games_played if latest_season else 0,
            } if latest_season else None,
            'stats': {
                'runs_scored': latest_stats.runs_scored if latest_stats else 0,
                'runs_allowed': latest_stats.runs_allowed if latest_stats else 0,
                'home_runs': latest_stats.home_runs if latest_stats else 0,
                'batting_average': float(latest_stats.batting_average) if latest_stats and latest_stats.batting_average else 0.0,
                'era': float(latest_stats.era) if latest_stats and latest_stats.era else 0.0,
            } if latest_stats else None,
        }
        
        return Response(profile_data)

class TeamSeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Team Seasons"""
    queryset = TeamSeason.objects.select_related('team', 'team__league', 'team__division').all()
    serializer_class = TeamSeasonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['season', 'team__abbreviation', 'team__league__abbreviation', 'team__division__abbreviation']
    search_fields = ['team__name', 'team__abbreviation']
    ordering_fields = ['season', 'wins', 'losses', 'winning_percentage']
    ordering = ['-season', 'team__name']

class TeamStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Team Stats"""
    queryset = TeamStats.objects.select_related('team').all()
    serializer_class = TeamStatsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['season', 'team__abbreviation', 'team__league__abbreviation']
    search_fields = ['team__name', 'team__abbreviation']
    ordering_fields = ['season', 'games_played', 'wins', 'losses', 'runs_scored', 'runs_allowed']
    ordering = ['-season', 'team__name']

    @action(detail=False, methods=['get'])
    def leaders(self, request):
        """Get team leaders in various statistical categories"""
        season = request.query_params.get('season')
        category = request.query_params.get('category', 'wins')
        
        stats_queryset = TeamStats.objects.select_related('team')
        if season:
            stats_queryset = stats_queryset.filter(season=season)
        
        # Define valid categories and their ordering
        valid_categories = {
            'wins': '-wins',
            'losses': '-losses',
            'runs_scored': '-runs_scored',
            'runs_allowed': 'runs_allowed',
            'home_runs': '-home_runs',
            'batting_average': '-batting_average',
            'era': 'era',
            'saves': '-saves'
        }
        
        if category in valid_categories:
            stats = stats_queryset.order_by(valid_categories[category])[:10]
        else:
            stats = stats_queryset.order_by('-wins')[:10]
        
        serializer = TeamStatsSerializer(stats, many=True)
        return Response(serializer.data)