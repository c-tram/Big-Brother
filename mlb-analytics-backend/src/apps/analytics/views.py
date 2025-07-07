from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Avg, Max, Min, Sum, Count
from decimal import Decimal
from .models import (
    PlayerAnalytics, PitcherAnalytics, GameAnalytics, 
    AdvancedTeamStats, TeamMatchup, SeasonTrend
)
from .serializers import (
    PlayerAnalyticsSerializer, PitcherAnalyticsSerializer, GameAnalyticsSerializer,
    AdvancedTeamStatsSerializer, TeamMatchupSerializer, SeasonTrendSerializer
)


class PlayerAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for advanced player analytics and sabermetrics.
    """
    queryset = PlayerAnalytics.objects.all()
    serializer_class = PlayerAnalyticsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['player', 'season', 'team']
    search_fields = ['player__first_name', 'player__last_name']
    ordering_fields = [
        'war', 'wrc_plus', 'babip', 'iso', 'woba', 'fip'
    ]
    ordering = ['-war']

    @action(detail=False, methods=['get'])
    def war_leaders(self, request):
        """Get WAR leaders for a season."""
        season = request.query_params.get('season', 2024)
        limit = int(request.query_params.get('limit', 10))
        
        analytics = self.get_queryset().filter(season=season).order_by('-war')[:limit]
        serializer = self.get_serializer(analytics, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def breakout_candidates(self, request):
        """Identify potential breakout candidates based on analytics."""
        season = request.query_params.get('season', 2024)
        
        # Simple breakout logic: high BABIP with low wRC+, suggesting bad luck
        candidates = self.get_queryset().filter(
            season=season,
            babip__gte=0.300,
            wrc_plus__lt=100,
            plate_appearances__gte=200
        ).order_by('-babip')
        
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)


class PitcherAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for advanced pitcher analytics and sabermetrics.
    """
    queryset = PitcherAnalytics.objects.all()
    serializer_class = PitcherAnalyticsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['player', 'season', 'team']
    search_fields = ['player__first_name', 'player__last_name']
    ordering_fields = [
        'war', 'fip', 'xfip', 'siera', 'k_minus_bb_percent'
    ]
    ordering = ['-war']

    @action(detail=False, methods=['get'])
    def cy_young_candidates(self, request):
        """Get potential Cy Young award candidates based on analytics."""
        season = request.query_params.get('season', 2024)
        league = request.query_params.get('league')
        
        queryset = self.get_queryset().filter(
            season=season,
            innings_pitched__gte=100
        ).order_by('-war')
        
        if league:
            queryset = queryset.filter(team__league__abbreviation=league)
        
        candidates = queryset[:10]
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def regression_candidates(self, request):
        """Identify pitchers due for regression based on luck indicators."""
        season = request.query_params.get('season', 2024)
        
        # Pitchers with low ERA but high FIP (getting lucky)
        candidates = self.get_queryset().filter(
            season=season,
            innings_pitched__gte=50
        ).extra(
            where=["fip - era > 0.75"]
        ).order_by('-fip')
        
        serializer = self.get_serializer(candidates, many=True)
        return Response(serializer.data)


class GameAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for individual game analytics and insights.
    """
    queryset = GameAnalytics.objects.all()
    serializer_class = GameAnalyticsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['game', 'win_probability_added__gt']
    ordering_fields = ['win_probability_added', 'leverage_index', 'championship_probability_added']
    ordering = ['-win_probability_added']

    @action(detail=False, methods=['get'])
    def high_leverage_games(self, request):
        """Get games with highest average leverage index."""
        min_leverage = float(request.query_params.get('min_leverage', 1.5))
        
        games = self.get_queryset().filter(
            leverage_index__gte=min_leverage
        ).order_by('-leverage_index')
        
        serializer = self.get_serializer(games, many=True)
        return Response(serializer.data)


class AdvancedTeamStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for advanced team statistics and analytics.
    """
    queryset = AdvancedTeamStats.objects.all()
    serializer_class = AdvancedTeamStatsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['team', 'season']
    ordering_fields = [
        'run_differential', 'pythagorean_wins', 'team_war', 'wrc_plus', 'fip'
    ]
    ordering = ['-team_war']

    @action(detail=False, methods=['get'])
    def playoff_odds(self, request):
        """Calculate playoff odds based on advanced metrics."""
        season = request.query_params.get('season', 2024)
        
        teams = self.get_queryset().filter(season=season).order_by('-pythagorean_wins')
        
        # Simple playoff odds calculation based on pythagorean wins
        for team_stat in teams:
            if team_stat.pythagorean_wins >= 90:
                team_stat.playoff_odds = 95
            elif team_stat.pythagorean_wins >= 85:
                team_stat.playoff_odds = 70
            elif team_stat.pythagorean_wins >= 80:
                team_stat.playoff_odds = 30
            else:
                team_stat.playoff_odds = 5
        
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def strength_of_schedule(self, request):
        """Get team strength of schedule metrics."""
        season = request.query_params.get('season', 2024)
        
        teams = self.get_queryset().filter(season=season).order_by('-strength_of_schedule')
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)


class TeamMatchupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for team head-to-head matchup analytics.
    """
    queryset = TeamMatchup.objects.all()
    serializer_class = TeamMatchupSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['team_a', 'team_b', 'season']
    ordering_fields = ['season', 'games_played', 'run_differential']
    ordering = ['-season']

    @action(detail=False, methods=['get'])
    def rivalry_matchups(self, request):
        """Get traditional rivalry matchups."""
        season = request.query_params.get('season', 2024)
        
        # Define some rivalry pairs (simplified)
        rivalry_pairs = [
            ('NYY', 'BOS'),  # Yankees vs Red Sox
            ('LAD', 'SF'),   # Dodgers vs Giants
            ('NYM', 'ATL'),  # Mets vs Braves
            ('CHC', 'STL'),  # Cubs vs Cardinals
        ]
        
        rivalries = []
        for team_a, team_b in rivalry_pairs:
            matchup = self.get_queryset().filter(
                season=season,
                team_a__abbreviation=team_a,
                team_b__abbreviation=team_b
            ).first()
            if matchup:
                rivalries.append(matchup)
        
        serializer = self.get_serializer(rivalries, many=True)
        return Response(serializer.data)


class SeasonTrendViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for analyzing season trends and performance over time.
    """
    queryset = SeasonTrend.objects.all()
    serializer_class = SeasonTrendSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['entity_type', 'entity_id', 'season', 'month']
    ordering_fields = ['season', 'month', 'metric_value']
    ordering = ['season', 'month']

    @action(detail=False, methods=['get'])
    def hot_cold_streaks(self, request):
        """Identify teams/players on hot or cold streaks."""
        entity_type = request.query_params.get('entity_type', 'team')
        streak_type = request.query_params.get('streak_type', 'hot')  # hot or cold
        season = request.query_params.get('season', 2024)
        
        queryset = self.get_queryset().filter(
            entity_type=entity_type,
            season=season,
            metric_name='winning_percentage'
        ).order_by('entity_id', 'month')
        
        # Calculate streak data (simplified)
        streaks = []
        current_entity = None
        current_trend = []
        
        for trend in queryset:
            if current_entity != trend.entity_id:
                if current_trend and len(current_trend) >= 2:
                    # Analyze trend
                    recent_performance = sum([t.metric_value for t in current_trend[-3:]])
                    if (streak_type == 'hot' and recent_performance > 1.8) or \
                       (streak_type == 'cold' and recent_performance < 1.2):
                        streaks.extend(current_trend[-3:])
                
                current_entity = trend.entity_id
                current_trend = [trend]
            else:
                current_trend.append(trend)
        
        serializer = self.get_serializer(streaks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def month_by_month(self, request):
        """Get month-by-month performance breakdown."""
        entity_type = request.query_params.get('entity_type')
        entity_id = request.query_params.get('entity_id')
        season = request.query_params.get('season', 2024)
        
        if not entity_type or not entity_id:
            return Response(
                {'error': 'entity_type and entity_id parameters are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trends = self.get_queryset().filter(
            entity_type=entity_type,
            entity_id=entity_id,
            season=season
        ).order_by('month')
        
        serializer = self.get_serializer(trends, many=True)
        return Response(serializer.data)