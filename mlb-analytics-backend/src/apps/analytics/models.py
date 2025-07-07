from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime, timedelta

class AdvancedTeamStats(models.Model):
    """Advanced team statistics and analytics"""
    team_season = models.OneToOneField('teams.TeamSeason', on_delete=models.CASCADE, related_name='advanced_stats')
    
    # Advanced offensive metrics
    team_ops_plus = models.IntegerField(null=True, blank=True)  # OPS+ (100 is average)
    team_wrc_plus = models.IntegerField(null=True, blank=True)  # wRC+ (100 is average)
    team_woba = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)  # Weighted On-Base Average
    
    # Advanced pitching metrics
    team_era_plus = models.IntegerField(null=True, blank=True)  # ERA+ (100 is average)
    team_fip = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Fielding Independent Pitching
    team_xfip = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Expected FIP
    
    # Base running
    base_running_runs = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stolen_base_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    # Clutch performance
    risp_batting_average = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)  # Runners in scoring position
    late_inning_pressure_avg = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    # Defensive metrics
    defensive_runs_saved = models.IntegerField(null=True, blank=True)
    ultimate_zone_rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Situational stats
    day_record = models.CharField(max_length=10, blank=True)  # W-L record in day games
    night_record = models.CharField(max_length=10, blank=True)  # W-L record in night games
    home_record = models.CharField(max_length=10, blank=True)
    away_record = models.CharField(max_length=10, blank=True)
    
    # Strength of schedule
    strength_of_schedule = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    class Meta:
        db_table = 'advanced_team_stats'
    
    def __str__(self):
        return f"{self.team_season.team} {self.team_season.season} Advanced Stats"

class PlayerAnalytics(models.Model):
    """Advanced player analytics and metrics"""
    player_season = models.OneToOneField('players.PlayerSeason', on_delete=models.CASCADE, related_name='analytics')
    
    # Advanced hitting metrics
    woba = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)  # Weighted On-Base Average
    wrc_plus = models.IntegerField(null=True, blank=True)  # Weighted Runs Created Plus
    babip = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)  # Batting Average on Balls in Play
    iso_power = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)  # Isolated Power
    
    # Plate discipline
    bb_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Walk percentage
    k_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Strikeout percentage
    bb_k_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Walk to strikeout ratio
    
    # Contact quality
    hard_hit_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ground_ball_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fly_ball_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    line_drive_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Situational performance
    risp_avg = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)  # Runners in scoring position
    bases_loaded_avg = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    two_out_risp_avg = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    # Defensive metrics (for position players)
    defensive_runs_saved = models.IntegerField(null=True, blank=True)
    ultimate_zone_rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    range_factor = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Base running
    base_running_runs = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stolen_base_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    class Meta:
        db_table = 'player_analytics'
    
    def __str__(self):
        return f"{self.player_season.player} {self.player_season.season} Analytics"

class PitcherAnalytics(models.Model):
    """Advanced pitcher analytics and metrics"""
    pitcher_season = models.OneToOneField('players.PitcherSeason', on_delete=models.CASCADE, related_name='analytics')
    
    # Advanced pitching metrics
    fip = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Fielding Independent Pitching
    xfip = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Expected FIP
    sierra = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Skill-Interactive ERA
    
    # Rate stats
    k_bb_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Strikeout to walk ratio
    k_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Strikeout percentage
    bb_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Walk percentage
    
    # Contact quality allowed
    hard_hit_percentage_against = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ground_ball_percentage_against = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fly_ball_percentage_against = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Luck factors
    babip_against = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    lob_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Left on base percentage
    hr_fb_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Home run to fly ball ratio
    
    # Situational performance
    risp_avg_against = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    first_inning_era = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Velocity and movement (if available)
    avg_fastball_velocity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_fastball_velocity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'pitcher_analytics'
    
    def __str__(self):
        return f"{self.pitcher_season.player} {self.pitcher_season.season} Pitching Analytics"

class GameAnalytics(models.Model):
    """Advanced game analytics and metrics"""
    game = models.OneToOneField('games.Game', on_delete=models.CASCADE, related_name='analytics')
    
    # Game flow metrics
    largest_lead_home = models.IntegerField(null=True, blank=True)
    largest_lead_away = models.IntegerField(null=True, blank=True)
    lead_changes = models.IntegerField(default=0)
    times_tied = models.IntegerField(default=0)
    
    # Leverage situations
    high_leverage_situations = models.IntegerField(default=0)
    clutch_hits = models.IntegerField(default=0)
    
    # Offensive efficiency
    home_team_risp_opportunities = models.IntegerField(default=0)
    away_team_risp_opportunities = models.IntegerField(default=0)
    home_team_risp_success = models.IntegerField(default=0)
    away_team_risp_success = models.IntegerField(default=0)
    
    # Pitching efficiency
    home_team_pitches_thrown = models.IntegerField(null=True, blank=True)
    away_team_pitches_thrown = models.IntegerField(null=True, blank=True)
    home_team_strikes_thrown = models.IntegerField(null=True, blank=True)
    away_team_strikes_thrown = models.IntegerField(null=True, blank=True)
    
    # Base running
    home_team_stolen_bases = models.IntegerField(default=0)
    away_team_stolen_bases = models.IntegerField(default=0)
    home_team_caught_stealing = models.IntegerField(default=0)
    away_team_caught_stealing = models.IntegerField(default=0)
    
    # Game characteristics
    extra_innings = models.BooleanField(default=False)
    walk_off_win = models.BooleanField(default=False)
    shutout = models.BooleanField(default=False)
    no_hitter = models.BooleanField(default=False)
    perfect_game = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'game_analytics'
    
    def __str__(self):
        return f"{self.game} Analytics"

class TeamMatchup(models.Model):
    """Historical matchup data between teams"""
    team_a = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='matchups_as_team_a')
    team_b = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='matchups_as_team_b')
    season = models.IntegerField()
    
    # Head-to-head record
    team_a_wins = models.IntegerField(default=0)
    team_b_wins = models.IntegerField(default=0)
    
    # Scoring
    team_a_runs_scored = models.IntegerField(default=0)
    team_b_runs_scored = models.IntegerField(default=0)
    team_a_runs_allowed = models.IntegerField(default=0)
    team_b_runs_allowed = models.IntegerField(default=0)
    
    # Games played
    total_games = models.IntegerField(default=0)
    home_games_team_a = models.IntegerField(default=0)
    home_games_team_b = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'team_matchups'
        unique_together = ['team_a', 'team_b', 'season']
    
    def __str__(self):
        return f"{self.team_a} vs {self.team_b} - {self.season}"

class SeasonTrend(models.Model):
    """Track trends and patterns throughout the season"""
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='trends')
    season = models.IntegerField()
    
    # Time period
    PERIOD_CHOICES = [
        ('month', 'Monthly'),
        ('week', 'Weekly'),
        ('last_10', 'Last 10 Games'),
        ('last_30', 'Last 30 Games'),
        ('home_stand', 'Home Stand'),
        ('road_trip', 'Road Trip'),
    ]
    
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Performance metrics
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    runs_scored = models.IntegerField(default=0)
    runs_allowed = models.IntegerField(default=0)
    
    # Trends
    batting_average = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    era = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Momentum indicators
    win_streak = models.IntegerField(default=0)
    loss_streak = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'season_trends'
        unique_together = ['team', 'season', 'period_type', 'period_start']
    
    def __str__(self):
        return f"{self.team} - {self.period_type} trend ({self.period_start})"