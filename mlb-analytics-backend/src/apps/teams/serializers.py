from rest_framework import serializers
from .models import Team, TeamSeason, TeamStats, League, Division, Venue

class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = '__all__'

class DivisionSerializer(serializers.ModelSerializer):
    league = LeagueSerializer(read_only=True)
    
    class Meta:
        model = Division
        fields = '__all__'

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    league = LeagueSerializer(read_only=True)
    division = DivisionSerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'

class TeamStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamStats
        fields = '__all__'

class TeamSeasonSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    stats = TeamStatsSerializer(read_only=True)
    
    class Meta:
        model = TeamSeason
        fields = '__all__'

class TeamSeasonListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_abbreviation = serializers.CharField(source='team.abbreviation', read_only=True)
    division_name = serializers.CharField(source='team.division.name', read_only=True)
    league_name = serializers.CharField(source='team.league.name', read_only=True)
    
    class Meta:
        model = TeamSeason
        fields = [
            'id', 'team_name', 'team_abbreviation', 'division_name', 'league_name',
            'season', 'wins', 'losses', 'games_played', 'win_percentage',
            'runs_scored', 'runs_allowed', 'run_differential', 'division_rank',
            'league_rank', 'games_back', 'streak_type', 'streak_number'
        ]

class TeamDetailSerializer(serializers.ModelSerializer):
    """Detailed team serializer with nested data"""
    league = LeagueSerializer(read_only=True)
    division = DivisionSerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    current_season = serializers.SerializerMethodField()
    recent_seasons = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = '__all__'
    
    def get_current_season(self, obj):
        from datetime import datetime
        current_year = datetime.now().year
        try:
            current_season = obj.seasons.get(season=current_year)
            return TeamSeasonSerializer(current_season).data
        except TeamSeason.DoesNotExist:
            return None
    
    def get_recent_seasons(self, obj):
        from datetime import datetime
        current_year = datetime.now().year
        recent_seasons = obj.seasons.filter(
            season__gte=current_year - 3,
            season__lte=current_year
        ).order_by('-season')[:4]
        return TeamSeasonListSerializer(recent_seasons, many=True).data

class StandingsSerializer(serializers.ModelSerializer):
    """Serializer for standings display"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    team_abbreviation = serializers.CharField(source='team.abbreviation', read_only=True)
    team_logo = serializers.URLField(source='team.logo_url', read_only=True, allow_null=True)
    
    class Meta:
        model = TeamSeason
        fields = [
            'id', 'team_name', 'team_abbreviation', 'team_logo',
            'wins', 'losses', 'win_percentage', 'games_back',
            'runs_scored', 'runs_allowed', 'run_differential',
            'streak_type', 'streak_number', 'division_rank',
            'elimination_number', 'magic_number'
        ]