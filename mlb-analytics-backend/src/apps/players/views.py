from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Avg, Max, Min
from .models import Player, PlayerTeamHistory, PlayerSeason, PitcherSeason, PlayerAward
from .serializers import (
    PlayerSerializer, PlayerTeamHistorySerializer, 
    PlayerSeasonSerializer, PitcherSeasonSerializer, PlayerAwardSerializer
)


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing MLB players with comprehensive filtering and search capabilities.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'primary_position', 'bat_side', 'pitch_hand', 'active', 'birth_country', 
        'birth_state_province', 'current_team'
    ]
    search_fields = [
        'first_name', 'last_name', 'full_name', 'birth_city', 
        'birth_country', 'birth_state_province'
    ]
    ordering_fields = [
        'last_name', 'first_name', 'birth_date', 'mlb_debut_date', 
        'height', 'weight', 'created_at'
    ]
    ordering = ['last_name', 'first_name']

    @action(detail=True, methods=['get'])
    def team_history(self, request, pk=None):
        """Get player's team history across seasons."""
        player = self.get_object()
        history = PlayerTeamHistory.objects.filter(player=player).order_by('-season')
        serializer = PlayerTeamHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def seasons(self, request, pk=None):
        """Get player's season statistics."""
        player = self.get_object()
        seasons = PlayerSeason.objects.filter(player=player).order_by('-season')
        serializer = PlayerSeasonSerializer(seasons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pitcher_seasons(self, request, pk=None):
        """Get pitcher's season statistics."""
        player = self.get_object()
        seasons = PitcherSeason.objects.filter(player=player).order_by('-season')
        serializer = PitcherSeasonSerializer(seasons, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def awards(self, request, pk=None):
        """Get player's awards and achievements."""
        player = self.get_object()
        awards = PlayerAward.objects.filter(player=player).order_by('-season')
        serializer = PlayerAwardSerializer(awards, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def position_leaders(self, request):
        """Get statistical leaders by position."""
        position = request.query_params.get('position')
        season = request.query_params.get('season', 2024)
        stat = request.query_params.get('stat', 'batting_average')
        
        if not position:
            return Response(
                {'error': 'Position parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get players at the specified position with season stats
        players = Player.objects.filter(
            position=position,
            playerseason__season=season
        ).select_related().prefetch_related('playerseason_set')
        
        # Order by the requested stat (simplified for now)
        if stat == 'batting_average':
            players = players.order_by('-playerseason__batting_average')
        elif stat == 'home_runs':
            players = players.order_by('-playerseason__home_runs')
        elif stat == 'rbi':
            players = players.order_by('-playerseason__rbi')
        
        serializer = PlayerSerializer(players[:10], many=True)  # Top 10
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def rookies(self, request):
        """Get rookie players for a given season."""
        season = request.query_params.get('season', 2024)
        
        rookies = Player.objects.filter(
            playerseason__season=season,
            playerseason__rookie_year=True
        ).distinct()
        
        serializer = PlayerSerializer(rookies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get complete player profile with stats"""
        player = self.get_object()
        season = request.query_params.get('season', 2024)
        
        # Get latest season data
        latest_season = PlayerSeason.objects.filter(player=player).order_by('-season').first()
        
        # Get current team - use start_date for ordering since PlayerTeamHistory doesn't have season
        current_team_history = PlayerTeamHistory.objects.filter(player=player).order_by('-start_date').first()
        
        profile_data = {
            'basicInfo': {
                'id': player.id,
                'fullName': player.full_name,
                'firstName': player.first_name,
                'lastName': player.last_name,
                'birthDate': player.birth_date.isoformat() if player.birth_date else None,
                'position': player.primary_position,
                'team': current_team_history.team.name if current_team_history and current_team_history.team else 'Free Agent',
                'jerseyNumber': getattr(player, 'jersey_number', None),
                'bats': player.bat_side,
                'throws': player.pitch_hand,
                'height': player.height,
                'weight': player.weight,
            },
            'currentSeasonStats': {
                'season': latest_season.season if latest_season else season,
                'games': latest_season.games_played if latest_season else 0,
                'atBats': latest_season.at_bats if latest_season else 0,
                'hits': latest_season.hits if latest_season else 0,
                'homeRuns': latest_season.home_runs if latest_season else 0,
                'rbis': latest_season.rbis if latest_season else 0,
                'average': float(latest_season.batting_average) if latest_season and latest_season.batting_average else 0.0,
                'ops': float(latest_season.ops) if latest_season and latest_season.ops else 0.0,
            } if latest_season else None,
            'careerStats': {
                'seasons': PlayerSeason.objects.filter(player=player).count(),
                'totalGames': sum(s.games_played for s in PlayerSeason.objects.filter(player=player) if s.games_played),
                'totalAtBats': sum(s.at_bats for s in PlayerSeason.objects.filter(player=player) if s.at_bats),
                'totalHits': sum(s.hits for s in PlayerSeason.objects.filter(player=player) if s.hits),
                'totalHomeRuns': sum(s.home_runs for s in PlayerSeason.objects.filter(player=player) if s.home_runs),
                'totalRbis': sum(s.rbis for s in PlayerSeason.objects.filter(player=player) if s.rbis),
            }
        }
        
        return Response(profile_data)


class PlayerTeamHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for player team history records.
    """
    queryset = PlayerTeamHistory.objects.all()
    serializer_class = PlayerTeamHistorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['player', 'team', 'season']
    ordering_fields = ['season', 'created_at']
    ordering = ['-season']


class PlayerSeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for player season statistics.
    """
    queryset = PlayerSeason.objects.all()
    serializer_class = PlayerSeasonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'player', 'team', 'season', 'league_id', 'rookie_year'
    ]
    ordering_fields = [
        'season', 'games', 'at_bats', 'hits', 'home_runs', 'rbi', 
        'batting_average', 'on_base_percentage', 'slugging_percentage'
    ]
    ordering = ['-season']

    @action(detail=False, methods=['get'])
    def leaders(self, request):
        """Get statistical leaders for batting stats."""
        season = request.query_params.get('season', 2024)
        stat = request.query_params.get('stat', 'batting_average')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset().filter(season=season)
        
        # Order by requested stat
        stat_mapping = {
            'batting_average': '-batting_average',
            'home_runs': '-home_runs',
            'rbi': '-rbi',
            'runs': '-runs',
            'hits': '-hits',
            'stolen_bases': '-stolen_bases',
            'on_base_percentage': '-on_base_percentage',
            'slugging_percentage': '-slugging_percentage'
        }
        
        if stat in stat_mapping:
            queryset = queryset.order_by(stat_mapping[stat])
        
        serializer = self.get_serializer(queryset[:limit], many=True)
        return Response(serializer.data)


class PitcherSeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for pitcher season statistics.
    """
    queryset = PitcherSeason.objects.all()
    serializer_class = PitcherSeasonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'player', 'team', 'season', 'league_id'
    ]
    ordering_fields = [
        'season', 'wins', 'losses', 'era', 'games', 'games_started',
        'innings_pitched', 'strikeouts', 'walks', 'saves'
    ]
    ordering = ['-season']

    @action(detail=False, methods=['get'])
    def leaders(self, request):
        """Get statistical leaders for pitching stats."""
        season = request.query_params.get('season', 2024)
        stat = request.query_params.get('stat', 'era')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset().filter(season=season)
        
        # Order by requested stat (note: ERA is ascending, others descending)
        stat_mapping = {
            'era': 'era',  # Lower is better
            'wins': '-wins',
            'strikeouts': '-strikeouts',
            'saves': '-saves',
            'innings_pitched': '-innings_pitched',
            'whip': 'whip',  # Lower is better
            'games': '-games',
            'complete_games': '-complete_games'
        }
        
        if stat in stat_mapping:
            queryset = queryset.order_by(stat_mapping[stat])
        
        serializer = self.get_serializer(queryset[:limit], many=True)
        return Response(serializer.data)


class PlayerAwardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for player awards and achievements.
    """
    queryset = PlayerAward.objects.all()
    serializer_class = PlayerAwardSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['player', 'award_type', 'season', 'league_id']
    ordering_fields = ['season', 'award_type', 'created_at']
    ordering = ['-season']

    @action(detail=False, methods=['get'])
    def by_award_type(self, request):
        """Get awards grouped by award type."""
        award_type = request.query_params.get('award_type')
        season = request.query_params.get('season')
        
        queryset = self.get_queryset()
        
        if award_type:
            queryset = queryset.filter(award_type=award_type)
        if season:
            queryset = queryset.filter(season=season)
        
        queryset = queryset.order_by('-season')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)