from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class League(models.Model):
    """MLB League model (AL/NL)"""
    mlb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    name_short = models.CharField(max_length=50)
    season_date_info = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'leagues'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Division(models.Model):
    """MLB Division model"""
    mlb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    name_short = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='divisions')
    
    class Meta:
        db_table = 'divisions'
        ordering = ['league__name', 'name']
    
    def __str__(self):
        return f"{self.league.abbreviation} {self.name}"

class Venue(models.Model):
    """MLB Venue/Stadium model"""
    mlb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, default='USA')
    
    # Location details
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    elevation = models.IntegerField(null=True, blank=True, help_text="Elevation in feet")
    
    # Stadium details
    capacity = models.IntegerField(null=True, blank=True)
    surface = models.CharField(max_length=50, blank=True)
    roof_type = models.CharField(max_length=50, blank=True)
    
    # Dimensions
    left_line = models.IntegerField(null=True, blank=True, help_text="Left field foul line distance")
    left_center = models.IntegerField(null=True, blank=True)
    center = models.IntegerField(null=True, blank=True, help_text="Center field distance")
    right_center = models.IntegerField(null=True, blank=True)
    right_line = models.IntegerField(null=True, blank=True, help_text="Right field foul line distance")
    
    # Metadata
    active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'venues'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.city})"

class Team(models.Model):
    """MLB Team model"""
    mlb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    team_name = models.CharField(max_length=100)  # e.g., "Yankees"
    location_name = models.CharField(max_length=100)  # e.g., "New York"
    
    # Identifiers
    abbreviation = models.CharField(max_length=5)
    team_code = models.CharField(max_length=5)
    file_code = models.CharField(max_length=5)
    
    # Relationships
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams')
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, related_name='teams')
    
    # Team details
    club_name = models.CharField(max_length=100, blank=True)
    short_name = models.CharField(max_length=50, blank=True)
    franchise_name = models.CharField(max_length=100, blank=True)
    
    # Seasons
    first_year_of_play = models.IntegerField(null=True, blank=True)
    
    # Status
    active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        ordering = ['division__league__name', 'division__name', 'name']
    
    def __str__(self):
        return f"{self.location_name} {self.team_name}"

class TeamSeason(models.Model):
    """Team season record and stats"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='seasons')
    season = models.IntegerField()
    
    # Record
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    
    # Advanced stats
    runs_scored = models.IntegerField(default=0)
    runs_allowed = models.IntegerField(default=0)
    run_differential = models.IntegerField(default=0)
    
    # Pythagorean expectation
    expected_wins = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    expected_losses = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Streak information
    streak_type = models.CharField(max_length=1, choices=[('W', 'Win'), ('L', 'Loss')], blank=True)
    streak_number = models.IntegerField(default=0)
    
    # Standings
    division_rank = models.IntegerField(null=True, blank=True)
    league_rank = models.IntegerField(null=True, blank=True)
    wild_card_rank = models.IntegerField(null=True, blank=True)
    
    # Advanced metrics
    games_back = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    wild_card_games_back = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Elimination/clinch info
    elimination_number = models.IntegerField(null=True, blank=True)
    magic_number = models.IntegerField(null=True, blank=True)
    
    # Calculated fields
    win_percentage = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    
    class Meta:
        db_table = 'team_seasons'
        unique_together = ['team', 'season']
        ordering = ['-season', 'team__division__league__name', 'team__division__name', 'team__name']
    
    def save(self, *args, **kwargs):
        # Calculate win percentage and other derived fields
        if self.games_played > 0:
            self.win_percentage = Decimal(str(self.wins / self.games_played))
        
        if self.runs_scored and self.runs_allowed:
            self.run_differential = self.runs_scored - self.runs_allowed
            
            # Calculate pythagorean expectation
            if self.runs_allowed > 0:
                pyth_exp = (self.runs_scored ** 2) / (self.runs_scored ** 2 + self.runs_allowed ** 2)
                self.expected_wins = Decimal(str(pyth_exp * self.games_played))
                self.expected_losses = Decimal(str(self.games_played)) - self.expected_wins
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.team} - {self.season}: {self.wins}W - {self.losses}L"

class TeamStats(models.Model):
    """Detailed team statistics"""
    team_season = models.OneToOneField(TeamSeason, on_delete=models.CASCADE, related_name='stats')
    
    # Batting stats
    batting_average = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    on_base_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    slugging_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    ops = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    hits = models.IntegerField(null=True, blank=True)
    doubles = models.IntegerField(null=True, blank=True)
    triples = models.IntegerField(null=True, blank=True)
    home_runs = models.IntegerField(null=True, blank=True)
    runs_batted_in = models.IntegerField(null=True, blank=True)
    walks = models.IntegerField(null=True, blank=True)
    strikeouts = models.IntegerField(null=True, blank=True)
    stolen_bases = models.IntegerField(null=True, blank=True)
    caught_stealing = models.IntegerField(null=True, blank=True)
    
    # Pitching stats
    earned_run_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    whip = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    innings_pitched = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    hits_allowed = models.IntegerField(null=True, blank=True)
    walks_allowed = models.IntegerField(null=True, blank=True)
    strikeouts_pitched = models.IntegerField(null=True, blank=True)
    home_runs_allowed = models.IntegerField(null=True, blank=True)
    
    saves = models.IntegerField(null=True, blank=True)
    blown_saves = models.IntegerField(null=True, blank=True)
    save_opportunities = models.IntegerField(null=True, blank=True)
    
    # Fielding stats
    fielding_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    errors = models.IntegerField(null=True, blank=True)
    double_plays = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'team_stats'
    
    def __str__(self):
        return f"{self.team_season.team} {self.team_season.season} Stats"