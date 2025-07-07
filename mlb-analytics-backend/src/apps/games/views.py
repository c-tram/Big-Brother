from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg, Sum
from datetime import datetime, timedelta
from .models import (
    Game, GameSeries, GameLineScore, GameEvent, 
    GamePlayerStats, GamePitcherStats
)
from .serializers import (
    GameSerializer, GameSeriesSerializer, GameLineScoreSerializer,
    GameEventSerializer, GamePlayerStatsSerializer, GamePitcherStatsSerializer
)


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing MLB games with comprehensive filtering and search capabilities.
    """
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'home_team', 'away_team', 'season', 'season_type', 'status', 
        'venue', 'game_date'
    ]
    search_fields = ['home_team__name', 'away_team__name', 'venue__name']
    ordering_fields = [
        'game_date', 'home_score', 'away_score', 
        'attendance', 'game_duration_minutes'
    ]
    ordering = ['-game_date']

    @action(detail=True, methods=['get'])
    def line_score(self, request, pk=None):
        """Get inning-by-inning line score for a game."""
        game = self.get_object()
        line_scores = GameLineScore.objects.filter(game=game).order_by('inning')
        serializer = GameLineScoreSerializer(line_scores, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get play-by-play events for a game."""
        game = self.get_object()
        events = GameEvent.objects.filter(game=game).order_by('inning', 'inning_half', 'at_bat_index')
        serializer = GameEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def player_stats(self, request, pk=None):
        """Get player batting statistics for a game."""
        game = self.get_object()
        stats = GamePlayerStats.objects.filter(game=game)
        serializer = GamePlayerStatsSerializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pitcher_stats(self, request, pk=None):
        """Get pitcher statistics for a game."""
        game = self.get_object()
        stats = GamePitcherStats.objects.filter(game=game)
        serializer = GamePitcherStatsSerializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's games."""
        today = datetime.now().date()
        games = self.get_queryset().filter(game_date=today)
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get games within a date range."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date parameters are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Date format should be YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        games = self.get_queryset().filter(
            game_date__range=[start_date, end_date]
        )
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def team_schedule(self, request):
        """Get schedule for a specific team."""
        team_id = request.query_params.get('team_id')
        season = request.query_params.get('season', 2024)
        
        if not team_id:
            return Response(
                {'error': 'team_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        games = self.get_queryset().filter(
            Q(home_team_id=team_id) | Q(away_team_id=team_id),
            season=season
        ).order_by('game_date')
        
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent completed games"""
        try:
            # Get games from the last 7 days that are completed
            recent_date = datetime.now() - timedelta(days=7)
            recent_games = Game.objects.filter(
                game_date__gte=recent_date.date(),
                status='final'
            ).select_related(
                'home_team', 'away_team', 'venue'
            ).order_by('-game_date', '-game_datetime')[:20]
            
            games_data = []
            for game in recent_games:
                games_data.append({
                    'id': game.id,
                    'gameId': game.mlb_game_pk,
                    'date': game.game_date.isoformat(),
                    'status': game.status,
                    'homeTeam': {
                        'id': game.home_team.id,
                        'name': game.home_team.name,
                        'abbreviation': game.home_team.abbreviation,
                    },
                    'awayTeam': {
                        'id': game.away_team.id,
                        'name': game.away_team.name,
                        'abbreviation': game.away_team.abbreviation,
                    },
                    'homeScore': game.home_score or 0,
                    'awayScore': game.away_score or 0,
                    'venue': {
                        'name': game.venue.name if game.venue else 'TBD',
                        'city': game.venue.city if game.venue else 'TBD',
                    } if game.venue else None,
                })
            
            return Response(games_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get recent games: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming scheduled games"""
        try:
            # Get games from the next 7 days
            upcoming_date = datetime.now() + timedelta(days=7)
            upcoming_games = Game.objects.filter(
                game_date__lte=upcoming_date.date(),
                game_date__gte=datetime.now().date(),
                status__in=['scheduled', 'pre_game']
            ).select_related(
                'home_team', 'away_team', 'venue'
            ).order_by('game_date', 'game_datetime')[:20]
            
            games_data = []
            for game in upcoming_games:
                games_data.append({
                    'id': game.id,
                    'gameId': game.mlb_game_pk,
                    'date': game.game_date.isoformat(),
                    'time': game.game_datetime.isoformat() if game.game_datetime else None,
                    'status': game.status,
                    'homeTeam': {
                        'id': game.home_team.id,
                        'name': game.home_team.name,
                        'abbreviation': game.home_team.abbreviation,
                    },
                    'awayTeam': {
                        'id': game.away_team.id,
                        'name': game.away_team.name,
                        'abbreviation': game.away_team.abbreviation,
                    },
                    'venue': {
                        'name': game.venue.name if game.venue else 'TBD',
                        'city': game.venue.city if game.venue else 'TBD',
                    } if game.venue else None,
                })
            
            return Response(games_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get upcoming games: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GameSeriesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for game series (e.g., 3-game series, playoff series).
    """
    queryset = GameSeries.objects.all()
    serializer_class = GameSeriesSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'home_team', 'away_team', 'season', 'series_type', 'playoff_round'
    ]
    ordering_fields = ['start_date', 'end_date', 'series_number']
    ordering = ['-start_date']

    @action(detail=True, methods=['get'])
    def games(self, request, pk=None):
        """Get all games in this series."""
        series = self.get_object()
        games = Game.objects.filter(series=series).order_by('game_date')
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)


class GameLineScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for inning-by-inning line scores.
    """
    queryset = GameLineScore.objects.all()
    serializer_class = GameLineScoreSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['game', 'inning']
    ordering_fields = ['inning']
    ordering = ['inning']


class GameEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for play-by-play game events.
    """
    queryset = GameEvent.objects.all()
    serializer_class = GameEventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'game', 'player', 'event_type', 'inning', 'inning_half'
    ]
    search_fields = ['event_description', 'player__full_name']
    ordering_fields = ['inning', 'inning_half', 'at_bat_index']
    ordering = ['inning', 'inning_half', 'at_bat_index']

    @action(detail=False, methods=['get'])
    def by_event_type(self, request):
        """Get events filtered by event type."""
        event_type = request.query_params.get('event_type')
        game_id = request.query_params.get('game_id')
        
        queryset = self.get_queryset()
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GamePlayerStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for player batting statistics in individual games.
    """
    queryset = GamePlayerStats.objects.all()
    serializer_class = GamePlayerStatsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'game', 'player', 'team', 'batting_order', 'position'
    ]
    ordering_fields = [
        'batting_order', 'at_bats', 'hits', 'runs', 'rbi', 'home_runs'
    ]
    ordering = ['batting_order']

    @action(detail=False, methods=['get'])
    def multi_hit_games(self, request):
        """Get games where players had multiple hits."""
        min_hits = int(request.query_params.get('min_hits', 2))
        
        stats = self.get_queryset().filter(hits__gte=min_hits)
        serializer = self.get_serializer(stats, many=True)
        return Response(serializer.data)


class GamePitcherStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for pitcher statistics in individual games.
    """
    queryset = GamePitcherStats.objects.all()
    serializer_class = GamePitcherStatsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'game', 'player', 'team', 'starter', 'win', 'loss', 'save'
    ]
    ordering_fields = [
        'innings_pitched', 'strikeouts', 'walks', 'hits_allowed', 'earned_runs'
    ]
    ordering = ['-innings_pitched']

    @action(detail=False, methods=['get'])
    def quality_starts(self, request):
        """Get quality starts (6+ innings, 3 or fewer earned runs)."""
        stats = self.get_queryset().filter(
            innings_pitched__gte=6.0,
            earned_runs__lte=3,
            starter=True
        )
        serializer = self.get_serializer(stats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def complete_games(self, request):
        """Get complete games pitched."""
        stats = self.get_queryset().filter(complete_game=True)
        serializer = self.get_serializer(stats, many=True)
        return Response(serializer.data)