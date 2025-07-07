from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date

class Player(models.Model):
    """MLB Player model"""
    
    # MLB API identifiers
    mlb_id = models.IntegerField(unique=True)
    
    # Personal information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    
    # Birth information
    birth_date = models.DateField(null=True, blank=True)
    birth_city = models.CharField(max_length=100, blank=True)
    birth_state_province = models.CharField(max_length=50, blank=True)
    birth_country = models.CharField(max_length=50, blank=True)
    
    # Physical characteristics
    height = models.CharField(max_length=10, blank=True)  # e.g., "6' 2\""
    weight = models.IntegerField(null=True, blank=True)
    
    # Playing information
    POSITION_CHOICES = [
        ('P', 'Pitcher'),
        ('C', 'Catcher'),
        ('1B', 'First Base'),
        ('2B', 'Second Base'),
        ('3B', 'Third Base'),
        ('SS', 'Shortstop'),
        ('LF', 'Left Field'),
        ('CF', 'Center Field'),
        ('RF', 'Right Field'),
        ('OF', 'Outfield'),
        ('IF', 'Infield'),
        ('DH', 'Designated Hitter'),
        ('UT', 'Utility'),
    ]
    
    primary_position = models.CharField(max_length=3, choices=POSITION_CHOICES, blank=True)
    
    BAT_SIDE_CHOICES = [
        ('L', 'Left'),
        ('R', 'Right'),
        ('S', 'Switch'),
    ]
    
    bat_side = models.CharField(max_length=1, choices=BAT_SIDE_CHOICES, blank=True)
    
    PITCH_HAND_CHOICES = [
        ('L', 'Left'),
        ('R', 'Right'),
    ]
    
    pitch_hand = models.CharField(max_length=1, choices=PITCH_HAND_CHOICES, blank=True)
    
    # Career information
    mlb_debut_date = models.DateField(null=True, blank=True)
    final_game_date = models.DateField(null=True, blank=True)
    
    # Current team
    current_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_players')
    
    # Status
    active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'players'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.primary_position}"
    
    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"

class PlayerTeamHistory(models.Model):
    """Track player's team history"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team_history')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='player_history')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Transaction type
    TRANSACTION_CHOICES = [
        ('draft', 'Draft'),
        ('trade', 'Trade'),
        ('free_agent', 'Free Agent'),
        ('waiver', 'Waiver Claim'),
        ('purchase', 'Purchase'),
        ('call_up', 'Call Up'),
        ('option', 'Option'),
        ('dfa', 'Designated for Assignment'),
        ('release', 'Release'),
        ('retirement', 'Retirement'),
    ]
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES, blank=True)
    
    class Meta:
        db_table = 'player_team_history'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.player} - {self.team} ({self.start_date})"

class PlayerSeason(models.Model):
    """Player's season statistics"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='seasons')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='player_seasons')
    season = models.IntegerField()
    
    # Game appearances
    games_played = models.IntegerField(default=0)
    games_started = models.IntegerField(default=0)
    
    # Basic stats
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
    
    # Advanced batting stats
    batting_average = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    on_base_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    slugging_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    ops = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    # Fielding stats
    fielding_percentage = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    errors = models.IntegerField(default=0)
    putouts = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'player_seasons'
        unique_together = ['player', 'team', 'season']
        ordering = ['-season', 'player__last_name', 'player__first_name']
    
    def save(self, *args, **kwargs):
        # Calculate batting average, OBP, SLG, and OPS
        if self.at_bats > 0:
            self.batting_average = Decimal(str(self.hits / self.at_bats))
            
            total_bases = (self.hits - self.doubles - self.triples - self.home_runs) + \
                         (self.doubles * 2) + (self.triples * 3) + (self.home_runs * 4)
            self.slugging_percentage = Decimal(str(total_bases / self.at_bats))
            
            plate_appearances = self.at_bats + self.walks
            if plate_appearances > 0:
                self.on_base_percentage = Decimal(str((self.hits + self.walks) / plate_appearances))
                
                if self.slugging_percentage and self.on_base_percentage:
                    self.ops = self.on_base_percentage + self.slugging_percentage
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.player} - {self.team} ({self.season})"

class PitcherSeason(models.Model):
    """Pitcher-specific season statistics"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='pitcher_seasons')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='pitcher_seasons')
    season = models.IntegerField()
    
    # Game appearances
    games_played = models.IntegerField(default=0)
    games_started = models.IntegerField(default=0)
    complete_games = models.IntegerField(default=0)
    shutouts = models.IntegerField(default=0)
    
    # Basic pitching stats
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    holds = models.IntegerField(default=0)
    blown_saves = models.IntegerField(default=0)
    save_opportunities = models.IntegerField(default=0)
    
    # Innings and outs
    innings_pitched = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    hits_allowed = models.IntegerField(default=0)
    runs_allowed = models.IntegerField(default=0)
    earned_runs = models.IntegerField(default=0)
    walks_allowed = models.IntegerField(default=0)
    strikeouts = models.IntegerField(default=0)
    home_runs_allowed = models.IntegerField(default=0)
    
    # Advanced pitching stats
    earned_run_average = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    whip = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    strikeouts_per_nine = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    walks_per_nine = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'pitcher_seasons'
        unique_together = ['player', 'team', 'season']
        ordering = ['-season', 'player__last_name', 'player__first_name']
    
    def save(self, *args, **kwargs):
        # Calculate ERA, WHIP, and rate stats
        if self.innings_pitched > 0:
            self.earned_run_average = Decimal(str((self.earned_runs * 9) / float(self.innings_pitched)))
            self.whip = Decimal(str((self.hits_allowed + self.walks_allowed) / float(self.innings_pitched)))
            self.strikeouts_per_nine = Decimal(str((self.strikeouts * 9) / float(self.innings_pitched)))
            self.walks_per_nine = Decimal(str((self.walks_allowed * 9) / float(self.innings_pitched)))
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.player} - {self.team} ({self.season}) Pitching"

class PlayerAward(models.Model):
    """Player awards and honors"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='awards')
    award_name = models.CharField(max_length=100)
    season = models.IntegerField()
    award_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'player_awards'
        unique_together = ['player', 'award_name', 'season']
        ordering = ['-season', 'award_name']
    
    def __str__(self):
        return f"{self.player} - {self.award_name} ({self.season})"