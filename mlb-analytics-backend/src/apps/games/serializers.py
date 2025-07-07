from rest_framework import serializers
from .models import (
    Game, GameSeries, GameLineScore, GameEvent, 
    GamePlayerStats, GamePitcherStats
)


class GameSerializer(serializers.ModelSerializer):
    """Serializer for Game model"""
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    
    class Meta:
        model = Game
        fields = '__all__'


class GameDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Game with all relationships"""
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    winning_pitcher_name = serializers.CharField(source='winning_pitcher.full_name', read_only=True)
    losing_pitcher_name = serializers.CharField(source='losing_pitcher.full_name', read_only=True)
    save_pitcher_name = serializers.CharField(source='save_pitcher.full_name', read_only=True)
    
    class Meta:
        model = Game
        fields = '__all__'


class GameSeriesSerializer(serializers.ModelSerializer):
    """Serializer for GameSeries model"""
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    
    class Meta:
        model = GameSeries
        fields = '__all__'


class GameLineScoreSerializer(serializers.ModelSerializer):
    """Serializer for GameLineScore model"""
    game_id = serializers.IntegerField(source='game.id', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = GameLineScore
        fields = '__all__'


class GameEventSerializer(serializers.ModelSerializer):
    """Serializer for GameEvent model"""
    game_id = serializers.IntegerField(source='game.id', read_only=True)
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    pitcher_name = serializers.CharField(source='pitcher.full_name', read_only=True)
    
    class Meta:
        model = GameEvent
        fields = '__all__'


class GamePlayerStatsSerializer(serializers.ModelSerializer):
    """Serializer for GamePlayerStats model"""
    game_id = serializers.IntegerField(source='game.id', read_only=True)
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = GamePlayerStats
        fields = '__all__'


class GamePitcherStatsSerializer(serializers.ModelSerializer):
    """Serializer for GamePitcherStats model"""
    game_id = serializers.IntegerField(source='game.id', read_only=True)
    pitcher_name = serializers.CharField(source='pitcher.full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = GamePitcherStats
        fields = '__all__'