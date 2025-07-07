"""
Management command to sync real MLB data from the official API
This bridges the gap between the MLB API service and our database models
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.teams.models import Team, Venue
from apps.players.models import Player
from apps.games.models import Game, GamePlayerStats
from services.mlb_api import MLBApi, MLBApiError
from datetime import datetime, timedelta
import json

class Command(BaseCommand):
    help = 'Sync real MLB data from official API into our database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--player-name',
            type=str,
            help='Specific player to sync (e.g., "Aaron Judge")'
        )
        parser.add_argument(
            '--venue-name', 
            type=str,
            help='Specific venue to filter games (e.g., "Dodger Stadium")'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=30,
            help='Number of days back to sync data (default: 30)'
        )
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season year to sync (default: 2024)'
        )

    def handle(self, *args, **options):
        player_name = options.get('player_name')
        venue_name = options.get('venue_name') 
        days_back = options['days_back']
        season = options['season']

        self.stdout.write("🔄 Starting MLB data sync...")
        self.stdout.write(f"Parameters: Player={player_name}, Venue={venue_name}, Days={days_back}, Season={season}")

        mlb_api = MLBApi()
        
        try:
            # Sync real data
            if player_name and venue_name:
                self.sync_player_venue_data(mlb_api, player_name, venue_name, days_back, season)
            else:
                self.sync_recent_games(mlb_api, days_back)
                
        except MLBApiError as e:
            self.stdout.write(self.style.ERROR(f"MLB API Error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def sync_player_venue_data(self, mlb_api, player_name, venue_name, days_back, season):
        """Sync specific player performance at specific venue"""
        self.stdout.write(f"\n🎯 Syncing {player_name} data at {venue_name}...")
        
        # Find player in our database
        player = self.find_player(player_name)
        if not player:
            self.stdout.write(self.style.ERROR(f"Player '{player_name}' not found in database"))
            return
            
        # Find venue in our database  
        venue = self.find_venue(venue_name)
        if not venue:
            self.stdout.write(self.style.ERROR(f"Venue '{venue_name}' not found in database"))
            return

        # Get team that plays at this venue
        home_team = Team.objects.filter(venue=venue).first()
        if not home_team:
            self.stdout.write(self.style.ERROR(f"No team found for venue '{venue_name}'"))
            return

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            # Get schedule for the player's team
            schedule_data = mlb_api.get_schedule(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                team_id=player.current_team.mlb_id if player.current_team else None
            )
            
            games_at_venue = []
            if 'dates' in schedule_data:
                for date_info in schedule_data['dates']:
                    for game in date_info.get('games', []):
                        venue_id = game.get('venue', {}).get('id')
                        if venue_id == venue.mlb_id:
                            games_at_venue.append(game)
            
            self.stdout.write(f"Found {len(games_at_venue)} games at {venue_name}")
            
            # Process each game
            for game_data in games_at_venue:
                self.process_game_with_player_stats(mlb_api, game_data, player, venue)
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing player venue data: {e}"))

    def sync_recent_games(self, mlb_api, days_back):
        """Sync recent games data"""
        self.stdout.write(f"\n📅 Syncing games from last {days_back} days...")
        
        try:
            games_data = mlb_api.get_date_range_games(days_back)
            
            if 'dates' in games_data:
                total_games = 0
                for date_info in games_data['dates']:
                    for game in date_info.get('games', []):
                        self.process_game(mlb_api, game)
                        total_games += 1
                        
                self.stdout.write(f"Processed {total_games} games")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing recent games: {e}"))

    def process_game_with_player_stats(self, mlb_api, game_data, player, venue):
        """Process a specific game and extract player stats"""
        game_id = game_data.get('gamePk')
        if not game_id:
            return
            
        try:
            # Get detailed game data
            detailed_game = mlb_api.get_game(game_id)
            boxscore = mlb_api.get_game_boxscore(game_id)
            
            # Create/update game in our database
            game = self.create_or_update_game(detailed_game, venue)
            
            # Extract player stats from boxscore
            player_stats = self.extract_player_stats(boxscore, player, game)
            
            if player_stats:
                self.stdout.write(f"  📊 {game.game_date}: {player.first_name} {player.last_name}")
                self.stdout.write(f"     Stats: {player_stats.hits}/{player_stats.at_bats}, {player_stats.home_runs} HR")
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error processing game {game_id}: {e}"))

    def process_game(self, mlb_api, game_data):
        """Process a general game"""
        game_id = game_data.get('gamePk')
        if not game_id:
            return
            
        try:
            # Check if game already exists
            if Game.objects.filter(mlb_game_id=game_id).exists():
                return
                
            detailed_game = mlb_api.get_game(game_id)
            self.create_or_update_game(detailed_game)
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error processing game {game_id}: {e}"))

    def create_or_update_game(self, game_data, venue=None):
        """Create or update game in database"""
        live_data = game_data.get('liveData', {})
        game_info = game_data.get('gameData', {})
        
        game_id = game_info.get('game', {}).get('pk')
        if not game_id:
            return None
            
        # Get teams
        teams = game_info.get('teams', {})
        home_team_id = teams.get('home', {}).get('id')
        away_team_id = teams.get('away', {}).get('id')
        
        home_team = Team.objects.filter(mlb_id=home_team_id).first()
        away_team = Team.objects.filter(mlb_id=away_team_id).first()
        
        if not home_team or not away_team:
            return None
            
        # Get or use venue
        if not venue:
            venue_id = game_info.get('venue', {}).get('id')
            venue = Venue.objects.filter(mlb_id=venue_id).first()
            
        # Get scores
        linescore = live_data.get('linescore', {})
        home_score = linescore.get('teams', {}).get('home', {}).get('runs', 0)
        away_score = linescore.get('teams', {}).get('away', {}).get('runs', 0)
        
        # Create game
        game, created = Game.objects.get_or_create(
            mlb_game_id=game_id,
            defaults={
                'game_date': datetime.strptime(game_info.get('datetime', {}).get('dateTime', '')[:10], '%Y-%m-%d').date(),
                'home_team': home_team,
                'away_team': away_team,
                'venue': venue,
                'home_score': home_score,
                'away_score': away_score,
                'inning': linescore.get('currentInning', 9),
                'game_status': game_info.get('status', {}).get('detailedState', 'Unknown'),
                'attendance': game_info.get('attendance', 0)
            }
        )
        
        return game

    def extract_player_stats(self, boxscore_data, player, game):
        """Extract specific player stats from boxscore"""
        try:
            teams = boxscore_data.get('teams', {})
            
            # Check both teams for the player
            for team_side in ['home', 'away']:
                team_data = teams.get(team_side, {})
                players = team_data.get('players', {})
                
                # Find player in this team's roster
                for player_key, player_data in players.items():
                    person = player_data.get('person', {})
                    if person.get('id') == player.mlb_id:
                        
                        # Get batting stats
                        stats = player_data.get('stats', {})
                        batting = stats.get('batting', {})
                        
                        if batting:
                            # Create player stats
                            team = game.home_team if team_side == 'home' else game.away_team
                            
                            player_stats, created = GamePlayerStats.objects.get_or_create(
                                game=game,
                                player=player,
                                team=team,
                                defaults={
                                    'at_bats': batting.get('atBats', 0),
                                    'runs': batting.get('runs', 0),
                                    'hits': batting.get('hits', 0),
                                    'rbis': batting.get('rbi', 0),
                                    'home_runs': batting.get('homeRuns', 0),
                                    'doubles': batting.get('doubles', 0),
                                    'triples': batting.get('triples', 0),
                                    'walks': batting.get('baseOnBalls', 0),
                                    'strikeouts': batting.get('strikeOuts', 0),
                                    'stolen_bases': batting.get('stolenBases', 0),
                                    'batting_average': batting.get('avg', 0.0),
                                    'on_base_percentage': batting.get('obp', 0.0),
                                    'slugging_percentage': batting.get('slg', 0.0)
                                }
                            )
                            
                            return player_stats
                            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error extracting player stats: {e}"))
            
        return None

    def find_player(self, player_name):
        """Find player in database"""
        parts = player_name.split()
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = ' '.join(parts[1:])
            return Player.objects.filter(
                first_name__icontains=first_name,
                last_name__icontains=last_name
            ).first()
        return Player.objects.filter(last_name__icontains=player_name).first()

    def find_venue(self, venue_name):
        """Find venue in database"""
        return Venue.objects.filter(name__icontains=venue_name).first()
