"""
Management command to load sample MLB games from the MLB API
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.teams.models import Team, Venue
from apps.games.models import Game, GameSeries
from services.mlb_api import MLBApi
import logging
from datetime import date, timedelta, datetime
import random

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load sample MLB games from MLB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season year to load data for (default: 2024)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days of games to load (default: 7)'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date in YYYY-MM-DD format (default: season start)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload of existing data'
        )

    def handle(self, *args, **options):
        season = options['season']
        days = options['days']
        start_date_str = options.get('start_date')
        force = options['force']
        
        if start_date_str:
            start_date = date.fromisoformat(start_date_str)
        else:
            start_date = date(season, 4, 1)  # Default season start
        
        self.stdout.write(f"Loading {days} days of MLB games starting from {start_date}...")
        
        try:
            with transaction.atomic():
                self.load_sample_games(start_date, days, force)
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded {days} days of MLB games')
            )
            
        except Exception as e:
            logger.error(f"Error loading MLB games: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error loading MLB games: {e}')
            )

    def load_sample_games(self, start_date, days, force):
        """Load sample MLB games"""
        self.stdout.write("Loading sample games...")
        
        teams = list(Team.objects.all())
        if len(teams) < 2:
            self.stdout.write(
                self.style.ERROR("Need at least 2 teams loaded to create games. Run load_teams command first.")
            )
            return
        
        created_count = 0
        
        for day_offset in range(days):
            game_date = start_date + timedelta(days=day_offset)
            
            # Skip if it's not a typical game day (very basic logic)
            if game_date.weekday() == 6:  # Skip some Sundays
                continue
            
            # Create 3-5 random games per day
            num_games = random.randint(3, 5)
            
            for game_num in range(num_games):
                # Select random teams
                home_team = random.choice(teams)
                away_team = random.choice([t for t in teams if t != home_team])
                
                # Generate realistic game data
                home_score = random.randint(0, 12)
                away_score = random.randint(0, 12)
                
                # Determine winner
                if home_score > away_score:
                    winning_team = home_team
                    losing_team = away_team
                elif away_score > home_score:
                    winning_team = away_team
                    losing_team = home_team
                else:
                    # Tie games are rare in MLB, make one team win
                    if random.choice([True, False]):
                        home_score += 1
                        winning_team = home_team
                        losing_team = away_team
                    else:
                        away_score += 1
                        winning_team = away_team
                        losing_team = home_team
                
                # Create unique game identifier
                game_mlb_id = int(f"{game_date.strftime('%Y%m%d')}{home_team.mlb_id}{game_num}")
                
                # Create game datetime (random time between 1 PM and 8 PM)
                game_hour = random.randint(13, 20)
                game_minute = random.choice([0, 15, 30, 45])
                game_datetime = datetime.combine(game_date, datetime.min.time().replace(hour=game_hour, minute=game_minute))
                
                # Create unique game GUID
                game_guid = f"{game_date.strftime('%Y%m%d')}-{home_team.abbreviation}-{away_team.abbreviation}-{game_num}"
                
                try:
                    game, created = Game.objects.get_or_create(
                        mlb_game_pk=game_mlb_id,
                        defaults={
                            'game_guid': game_guid,
                            'game_date': game_date,
                            'game_datetime': game_datetime,
                            'home_team': home_team,
                            'away_team': away_team,
                            'venue': home_team.venue,
                            'home_score': home_score,
                            'away_score': away_score,
                            'status': 'final',
                            'season': game_date.year,
                            'season_type': 'Regular Season',
                            'current_inning': 9,
                            'inning_state': 'Bottom' if winning_team == home_team else 'Top',
                            'attendance': random.randint(15000, 45000),
                            'weather_temp': random.randint(45, 85),
                            'weather_condition': random.choice(['Clear', 'Cloudy', 'Partly Cloudy', 'Overcast']),
                            'wind_speed': random.randint(0, 15),
                            'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
                            'game_duration_minutes': random.randint(150, 210),
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            f"  Created: {game_date} - {away_team.abbreviation} @ {home_team.abbreviation} "
                            f"({away_score}-{home_score})"
                        )
                    elif force:
                        # Update existing game
                        game.home_score = home_score
                        game.away_score = away_score
                        game.save()
                        self.stdout.write(
                            f"  Updated: {game_date} - {away_team.abbreviation} @ {home_team.abbreviation} "
                            f"({away_score}-{home_score})"
                        )
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error creating game {game_mlb_id}: {e}")
                    )
                    continue
        
        self.stdout.write(f"Created {created_count} games")
