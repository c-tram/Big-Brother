"""
Management command to load specific player performance data at specific venues
Example: Aaron Judge hitting at Dodger Stadium
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.players.models import Player
from apps.teams.models import Team, Venue
from apps.games.models import Game, GamePlayerStats
from services.mlb_api import MLBApi
import random
from datetime import datetime, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Load player performance data at specific venues (example: Aaron Judge at Dodger Stadium)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--player-name',
            type=str,
            default='Aaron Judge',
            help='Player name to load stats for'
        )
        parser.add_argument(
            '--venue-name',
            type=str,
            default='Dodger Stadium',
            help='Venue name to load stats for'
        )
        parser.add_argument(
            '--games',
            type=int,
            default=5,
            help='Number of games to simulate'
        )

    def handle(self, *args, **options):
        player_name = options['player_name']
        venue_name = options['venue_name']
        num_games = options['games']
        
        self.stdout.write(f"Loading {player_name} performance data at {venue_name}...")
        
        try:
            with transaction.atomic():
                # Get player and venue
                player = self.get_player(player_name)
                venue = self.get_venue(venue_name)
                
                if not player:
                    self.stdout.write(self.style.ERROR(f"Player '{player_name}' not found"))
                    return
                    
                if not venue:
                    self.stdout.write(self.style.ERROR(f"Venue '{venue_name}' not found"))
                    return
                
                # Get teams
                visiting_team = player.current_team
                home_team = self.get_team_by_venue(venue)
                
                # Create games and stats
                games_created = self.create_games_and_stats(
                    player, venue, visiting_team, home_team, num_games
                )
                
                # Display results
                self.display_results(player, venue, games_created)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def get_player(self, name):
        """Get player by name"""
        parts = name.split()
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = ' '.join(parts[1:])
            return Player.objects.filter(
                first_name__icontains=first_name,
                last_name__icontains=last_name
            ).first()
        return Player.objects.filter(last_name__icontains=name).first()

    def get_venue(self, name):
        """Get venue by name"""
        return Venue.objects.filter(name__icontains=name).first()

    def get_team_by_venue(self, venue):
        """Get the team that plays at this venue"""
        return Team.objects.filter(venue=venue).first()

    def create_games_and_stats(self, player, venue, visiting_team, home_team, num_games):
        """Create realistic games and player stats"""
        games_created = []
        base_date = datetime.now() - timedelta(days=365)  # Start from a year ago
        
        for i in range(num_games):
            # Create game
            game_date = base_date + timedelta(days=random.randint(0, 300))
            
            game = Game.objects.create(
                game_date=game_date.date(),
                home_team=home_team,
                away_team=visiting_team,
                venue=venue,
                home_score=random.randint(2, 12),
                away_score=random.randint(1, 10),
                inning=9,
                game_status='Final',
                attendance=random.randint(35000, 52000),
                weather_temp=random.randint(65, 85),
                weather_condition='Clear',
                game_time_minutes=random.randint(150, 200)
            )
            
            # Create Aaron Judge's stats for this game
            at_bats = random.randint(3, 5)
            hits = random.randint(0, min(at_bats, 3))  # Realistic hit rate
            home_runs = random.randint(0, min(hits, 2)) if hits > 0 else 0
            rbis = random.randint(0, 4) if hits > 0 else random.randint(0, 1)
            
            player_stats = GamePlayerStats.objects.create(
                game=game,
                player=player,
                team=visiting_team,
                at_bats=at_bats,
                runs=random.randint(0, 2),
                hits=hits,
                rbis=rbis,
                home_runs=home_runs,
                stolen_bases=random.randint(0, 1),
                walks=random.randint(0, 2),
                strikeouts=random.randint(0, at_bats - hits),
                doubles=random.randint(0, hits - home_runs) if hits > home_runs else 0,
                triples=0,  # Rare for power hitters
                batting_average=Decimal(str(round(hits / at_bats if at_bats > 0 else 0, 3))),
                on_base_percentage=Decimal(str(round((hits + random.randint(0, 2)) / (at_bats + random.randint(0, 2)) if at_bats > 0 else 0, 3))),
                slugging_percentage=Decimal(str(round((hits + home_runs * 3) / at_bats if at_bats > 0 else 0, 3)))
            )
            
            games_created.append({
                'game': game,
                'stats': player_stats
            })
            
            self.stdout.write(f"  Created game {i+1}: {game.away_team.abbreviation} @ {game.home_team.abbreviation} on {game.game_date}")
            self.stdout.write(f"    Judge: {hits}/{at_bats}, {home_runs} HR, {rbis} RBI")
        
        return games_created

    def display_results(self, player, venue, games_created):
        """Display comprehensive results"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"🏟️  {player.first_name} {player.last_name} at {venue.name}"))
        self.stdout.write("="*60)
        
        # Calculate totals
        total_games = len(games_created)
        total_at_bats = sum(g['stats'].at_bats for g in games_created)
        total_hits = sum(g['stats'].hits for g in games_created)
        total_home_runs = sum(g['stats'].home_runs for g in games_created)
        total_rbis = sum(g['stats'].rbis for g in games_created)
        total_runs = sum(g['stats'].runs for g in games_created)
        total_walks = sum(g['stats'].walks for g in games_created)
        total_strikeouts = sum(g['stats'].strikeouts for g in games_created)
        
        # Calculate averages
        avg = total_hits / total_at_bats if total_at_bats > 0 else 0
        
        self.stdout.write(f"\n📊 PERFORMANCE SUMMARY:")
        self.stdout.write(f"  Games Played: {total_games}")
        self.stdout.write(f"  At Bats: {total_at_bats}")
        self.stdout.write(f"  Hits: {total_hits}")
        self.stdout.write(f"  Batting Average: {avg:.3f}")
        self.stdout.write(f"  Home Runs: {total_home_runs}")
        self.stdout.write(f"  RBIs: {total_rbis}")
        self.stdout.write(f"  Runs: {total_runs}")
        self.stdout.write(f"  Walks: {total_walks}")
        self.stdout.write(f"  Strikeouts: {total_strikeouts}")
        
        self.stdout.write(f"\n📍 VENUE INFO:")
        self.stdout.write(f"  Stadium: {venue.name}")
        self.stdout.write(f"  City: {venue.city}, {venue.state}")
        self.stdout.write(f"  Capacity: {venue.capacity:,}")
        
        self.stdout.write(f"\n🎯 GAME-BY-GAME BREAKDOWN:")
        for i, game_data in enumerate(games_created, 1):
            game = game_data['game']
            stats = game_data['stats']
            self.stdout.write(f"  Game {i}: {game.game_date} - {stats.hits}/{stats.at_bats}")
            if stats.home_runs > 0:
                self.stdout.write(f"    💥 {stats.home_runs} Home Run{'s' if stats.home_runs > 1 else ''}!")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✅ Data loading complete!"))
        self.stdout.write("="*60)
