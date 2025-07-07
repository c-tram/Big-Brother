from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime

class Game(models.Model):
    """MLB Game model"""
    
    # MLB API identifiers
    mlb_game_pk = models.IntegerField(unique=True)
    game_guid = models.CharField(max_length=100, unique=True)
    
    # Game information
    game_date = models.DateField()
    game_datetime = models.DateTimeField()
    
    # Teams
    home_team = models.ForeignKey('teams.Team', related_name='home_games', on_delete=models.CASCADE)
    away_team = models.ForeignKey('teams.Team', related_name='away_games', on_delete=models.CASCADE)
    
    # Venue
    venue = models.ForeignKey('teams.Venue', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Season information
    season = models.IntegerField()
    season_type = models.CharField(max_length=20, default='Regular Season')
    
    # Game status
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('pre_game', 'Pre-Game'),
        ('warmup', 'Warmup'),
        ('in_progress', 'In Progress'),
        ('final', 'Final'),
        ('completed_early', 'Completed Early'),
        ('suspended', 'Suspended'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    detailed_state = models.CharField(max_length=50, blank=True)
    
    # Scores
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    
    # Innings
    current_inning = models.IntegerField(null=True, blank=True)
    inning_state = models.CharField(max_length=10, blank=True)  # 'Top', 'Bottom', 'Middle'
    
    # Game length
    game_duration_minutes = models.IntegerField(null=True, blank=True)
    
    # Weather
    weather_condition = models.CharField(max_length=100, blank=True)
    weather_temp = models.IntegerField(null=True, blank=True)
    wind_speed = models.CharField(max_length=20, blank=True)
    wind_direction = models.CharField(max_length=20, blank=True)
    
    # Attendance
    attendance = models.IntegerField(null=True, blank=True)
    
    # Umpires
    home_plate_umpire = models.CharField(max_length=100, blank=True)
    first_base_umpire = models.CharField(max_length=100, blank=True)
    second_base_umpire = models.CharField(max_length=100, blank=True)
    third_base_umpire = models.CharField(max_length=100, blank=True)
    
    # Game notes
    day_night = models.CharField(max_length=10, blank=True)  # 'day', 'night'
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'games'
        ordering = ['-game_date', '-game_datetime']
        indexes = [
            models.Index(fields=['game_date']),
            models.Index(fields=['season']),
            models.Index(fields=['home_team', 'game_date']),
            models.Index(fields=['away_team', 'game_date']),
        ]
    
    def __str__(self):
        return f"{self.away_team} @ {self.home_team} - {self.game_date}"
    
    @property
    def winning_team(self):
        if self.home_score is not None and self.away_score is not None:
            if self.home_score > self.away_score:
                return self.home_team
            elif self.away_score > self.home_score:
                return self.away_team
        return None
    
    @property
    def losing_team(self):
        if self.home_score is not None and self.away_score is not None:
            if self.home_score > self.away_score:
                return self.away_team
            elif self.away_score > self.home_score:
                return self.home_team
        return None
    
    @property
    def is_final(self):
        return self.status in ['final', 'completed_early']

class GameLineScore(models.Model):
    """Game line score by inning"""
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='line_score')
    
    # Inning-by-inning scores stored as JSON
    home_line_score = models.JSONField(default=list)  # List of runs by inning
    away_line_score = models.JSONField(default=list)  # List of runs by inning
    
    # Totals
    home_runs = models.IntegerField(default=0)
    away_runs = models.IntegerField(default=0)
    home_hits = models.IntegerField(default=0)
    away_hits = models.IntegerField(default=0)
    home_errors = models.IntegerField(default=0)
    away_errors = models.IntegerField(default=0)
    home_left_on_base = models.IntegerField(default=0)
    away_left_on_base = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'game_line_scores'
    
    def __str__(self):
        return f"{self.game} Line Score"

class GamePlayerStats(models.Model):
    """Individual player stats for a game"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='player_stats')
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    
    # Position and batting order
    position = models.CharField(max_length=3, blank=True)
    batting_order = models.IntegerField(null=True, blank=True)
    
    # Batting stats
    at_bats = models.IntegerField(default=0)
    runs = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)
    doubles = models.IntegerField(default=0)
    triples = models.IntegerField(default=0)
    home_runs = models.IntegerField(default=0)
    runs_batted_in = models.IntegerField(default=0)
    walks = models.IntegerField(default=0)
    strikeouts = models.IntegerField(default=0)
    stolen_bases = models.IntegerField(default=0)
    caught_stealing = models.IntegerField(default=0)
    
    # Fielding stats
    putouts = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'game_player_stats'
        unique_together = ['game', 'player']
    
    def __str__(self):
        return f"{self.player} - {self.game}"

class GamePitcherStats(models.Model):
    """Pitcher stats for a game"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='pitcher_stats')
    player = models.ForeignKey('players.Player', on_delete=models.CASCADE)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)
    
    # Pitching role
    PITCHER_ROLE_CHOICES = [
        ('starter', 'Starting Pitcher'),
        ('reliever', 'Relief Pitcher'),
        ('closer', 'Closer'),
    ]
    
    role = models.CharField(max_length=20, choices=PITCHER_ROLE_CHOICES, blank=True)
    
    # Decision
    DECISION_CHOICES = [
        ('W', 'Win'),
        ('L', 'Loss'),
        ('S', 'Save'),
        ('H', 'Hold'),
        ('BS', 'Blown Save'),
        ('', 'No Decision'),
    ]
    
    decision = models.CharField(max_length=2, choices=DECISION_CHOICES, blank=True)
    
    # Pitching stats
    innings_pitched = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    hits_allowed = models.IntegerField(default=0)
    runs_allowed = models.IntegerField(default=0)
    earned_runs = models.IntegerField(default=0)
    walks_allowed = models.IntegerField(default=0)
    strikeouts = models.IntegerField(default=0)
    home_runs_allowed = models.IntegerField(default=0)
    
    # Advanced stats
    pitches_thrown = models.IntegerField(null=True, blank=True)
    strikes_thrown = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'game_pitcher_stats'
        unique_together = ['game', 'player']
    
    def __str__(self):
        return f"{self.player} - {self.game} Pitching"

class GameSeries(models.Model):
    """Series information for games"""
    series_id = models.CharField(max_length=50, unique=True)
    home_team = models.ForeignKey('teams.Team', related_name='home_series', on_delete=models.CASCADE)
    away_team = models.ForeignKey('teams.Team', related_name='away_series', on_delete=models.CASCADE)
    
    # Series details
    series_description = models.CharField(max_length=200, blank=True)
    series_game_number = models.IntegerField(null=True, blank=True)
    series_games_total = models.IntegerField(null=True, blank=True)
    
    # Dates
    series_start_date = models.DateField()
    series_end_date = models.DateField()
    
    class Meta:
        db_table = 'game_series'
        ordering = ['series_start_date']
    
    def __str__(self):
        return f"{self.away_team} @ {self.home_team} Series"

class GameEvent(models.Model):
    """Individual game events (plays, at-bats, etc.)"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='events')
    
    # Event details
    inning = models.IntegerField()
    inning_half = models.CharField(max_length=10)  # 'top', 'bottom'
    event_sequence = models.IntegerField()  # Order of events in game
    
    # Players involved
    batter = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='batting_events')
    pitcher = models.ForeignKey('players.Player', on_delete=models.CASCADE, related_name='pitching_events')
    
    # Event type and description
    event_type = models.CharField(max_length=50)  # 'single', 'strikeout', 'walk', etc.
    event_description = models.TextField(blank=True)
    
    # Game state
    balls = models.IntegerField(default=0)
    strikes = models.IntegerField(default=0)
    outs = models.IntegerField(default=0)
    
    # Runs scored on this play
    runs_scored = models.IntegerField(default=0)
    
    # Base runners
    runner_on_first = models.ForeignKey('players.Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='first_base_events')
    runner_on_second = models.ForeignKey('players.Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='second_base_events')
    runner_on_third = models.ForeignKey('players.Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='third_base_events')
    
    class Meta:
        db_table = 'game_events'
        ordering = ['game', 'inning', 'event_sequence']
    
    def __str__(self):
        return f"{self.game} - Inning {self.inning} - {self.event_type}"