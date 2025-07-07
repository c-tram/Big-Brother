from rest_framework import serializers
from .models import Player, PlayerTeamHistory, PlayerSeason, PitcherSeason, PlayerAward


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model with basic information"""
    current_team_name = serializers.CharField(source='current_team.name', read_only=True)
    
    class Meta:
        model = Player
        fields = '__all__'


class PlayerDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Player with nested relationships"""
    current_team_name = serializers.CharField(source='current_team.name', read_only=True)
    
    class Meta:
        model = Player
        fields = '__all__'


class PlayerTeamHistorySerializer(serializers.ModelSerializer):
    """Serializer for PlayerTeamHistory model"""
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = PlayerTeamHistory
        fields = '__all__'


class PlayerSeasonSerializer(serializers.ModelSerializer):
    """Serializer for PlayerSeason model with batting statistics"""
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    batting_average = serializers.SerializerMethodField()
    on_base_percentage = serializers.SerializerMethodField()
    slugging_percentage = serializers.SerializerMethodField()
    ops = serializers.SerializerMethodField()
    
    class Meta:
        model = PlayerSeason
        fields = '__all__'
    
    def get_batting_average(self, obj):
        """Calculate batting average"""
        if obj.at_bats == 0:
            return 0.000
        return round(obj.hits / obj.at_bats, 3)
    
    def get_on_base_percentage(self, obj):
        """Calculate on-base percentage"""
        plate_appearances = obj.at_bats + obj.walks + obj.hit_by_pitch + obj.sacrifice_flies
        if plate_appearances == 0:
            return 0.000
        return round((obj.hits + obj.walks + obj.hit_by_pitch) / plate_appearances, 3)
    
    def get_slugging_percentage(self, obj):
        """Calculate slugging percentage"""
        if obj.at_bats == 0:
            return 0.000
        total_bases = obj.hits + obj.doubles + (obj.triples * 2) + (obj.home_runs * 3)
        return round(total_bases / obj.at_bats, 3)
    
    def get_ops(self, obj):
        """Calculate OPS (On-base Plus Slugging)"""
        obp = self.get_on_base_percentage(obj)
        slg = self.get_slugging_percentage(obj)
        return round(obp + slg, 3)


class PitcherSeasonSerializer(serializers.ModelSerializer):
    """Serializer for PitcherSeason model with pitching statistics"""
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    era = serializers.SerializerMethodField()
    whip = serializers.SerializerMethodField()
    k_per_9 = serializers.SerializerMethodField()
    bb_per_9 = serializers.SerializerMethodField()
    
    class Meta:
        model = PitcherSeason
        fields = '__all__'
    
    def get_era(self, obj):
        """Calculate ERA"""
        if obj.innings_pitched == 0:
            return 0.00
        return round((obj.earned_runs * 9) / obj.innings_pitched, 2)
    
    def get_whip(self, obj):
        """Calculate WHIP (Walks + Hits per Inning Pitched)"""
        if obj.innings_pitched == 0:
            return 0.00
        return round((obj.walks + obj.hits_allowed) / obj.innings_pitched, 2)
    
    def get_k_per_9(self, obj):
        """Calculate strikeouts per 9 innings"""
        if obj.innings_pitched == 0:
            return 0.00
        return round((obj.strikeouts * 9) / obj.innings_pitched, 2)
    
    def get_bb_per_9(self, obj):
        """Calculate walks per 9 innings"""
        if obj.innings_pitched == 0:
            return 0.00
        return round((obj.walks * 9) / obj.innings_pitched, 2)


class PlayerAwardSerializer(serializers.ModelSerializer):
    """Serializer for PlayerAward model"""
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    
    class Meta:
        model = PlayerAward
        fields = '__all__'