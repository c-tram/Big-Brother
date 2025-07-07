from rest_framework import serializers
from .models import (
    PlayerAnalytics, PitcherAnalytics, GameAnalytics, 
    AdvancedTeamStats, TeamMatchup, SeasonTrend
)


class PlayerAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for PlayerAnalytics model with advanced metrics"""
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = PlayerAnalytics
        fields = '__all__'


class PitcherAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for PitcherAnalytics model with advanced pitching metrics"""
    pitcher_name = serializers.CharField(source='pitcher.full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = PitcherAnalytics
        fields = '__all__'


class GameAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for GameAnalytics model"""
    game_id = serializers.IntegerField(source='game.id', read_only=True)
    home_team_name = serializers.CharField(source='game.home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='game.away_team.name', read_only=True)
    
    class Meta:
        model = GameAnalytics
        fields = '__all__'


class AdvancedTeamStatsSerializer(serializers.ModelSerializer):
    """Serializer for AdvancedTeamStats model"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = AdvancedTeamStats
        fields = '__all__'


class TeamMatchupSerializer(serializers.ModelSerializer):
    """Serializer for TeamMatchup model"""
    team1_name = serializers.CharField(source='team1.name', read_only=True)
    team2_name = serializers.CharField(source='team2.name', read_only=True)
    
    class Meta:
        model = TeamMatchup
        fields = '__all__'


class SeasonTrendSerializer(serializers.ModelSerializer):
    """Serializer for SeasonTrend model"""
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = SeasonTrend
        fields = '__all__'