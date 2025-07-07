"""
Master management command to load all MLB data in the correct order
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load all MLB data (teams, players, games) in the correct order'

    def add_arguments(self, parser):
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season year to load data for (default: 2024)'
        )
        parser.add_argument(
            '--player-limit',
            type=int,
            default=50,
            help='Limit number of players to load (default: 50)'
        )
        parser.add_argument(
            '--game-days',
            type=int,
            default=7,
            help='Number of days of games to load (default: 7)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload of existing data'
        )
        parser.add_argument(
            '--skip-teams',
            action='store_true',
            help='Skip loading teams data'
        )
        parser.add_argument(
            '--skip-players',
            action='store_true',
            help='Skip loading players data'
        )
        parser.add_argument(
            '--skip-games',
            action='store_true',
            help='Skip loading games data'
        )

    def handle(self, *args, **options):
        season = options['season']
        player_limit = options['player_limit']
        game_days = options['game_days']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting MLB data load for {season} season...')
        )
        
        try:
            # Step 1: Load teams (leagues, divisions, venues, teams)
            if not options['skip_teams']:
                self.stdout.write("\n" + "="*50)
                self.stdout.write("STEP 1: Loading Teams Data")
                self.stdout.write("="*50)
                call_command('load_teams', season=season, force=force, verbosity=1)
            
            # Step 2: Load players
            if not options['skip_players']:
                self.stdout.write("\n" + "="*50)
                self.stdout.write("STEP 2: Loading Players Data")
                self.stdout.write("="*50)
                call_command('load_players', season=season, limit=player_limit, force=force, verbosity=1)
            
            # Step 3: Load games
            if not options['skip_games']:
                self.stdout.write("\n" + "="*50)
                self.stdout.write("STEP 3: Loading Games Data")
                self.stdout.write("="*50)
                call_command('load_games', season=season, days=game_days, force=force, verbosity=1)
            
            self.stdout.write("\n" + "="*50)
            self.stdout.write(
                self.style.SUCCESS(f'✅ MLB data load completed successfully for {season}!')
            )
            self.stdout.write("="*50)
            
            # Show summary
            self.show_data_summary()
            
        except Exception as e:
            logger.error(f"Error during MLB data load: {e}")
            self.stdout.write(
                self.style.ERROR(f'❌ Error during MLB data load: {e}')
            )

    def show_data_summary(self):
        """Show a summary of loaded data"""
        from apps.teams.models import League, Division, Venue, Team
        from apps.players.models import Player
        from apps.games.models import Game
        
        self.stdout.write("\n📊 Data Summary:")
        self.stdout.write(f"  • Leagues: {League.objects.count()}")
        self.stdout.write(f"  • Divisions: {Division.objects.count()}")
        self.stdout.write(f"  • Venues: {Venue.objects.count()}")
        self.stdout.write(f"  • Teams: {Team.objects.count()}")
        self.stdout.write(f"  • Players: {Player.objects.count()}")
        self.stdout.write(f"  • Games: {Game.objects.count()}")
        
        self.stdout.write("\n🔗 API Endpoints Available:")
        self.stdout.write("  • http://localhost:8000/api/v1/teams/")
        self.stdout.write("  • http://localhost:8000/api/v1/players/")
        self.stdout.write("  • http://localhost:8000/api/v1/games/")
        self.stdout.write("  • http://localhost:8000/api/v1/analytics/")
        self.stdout.write("\n🚀 Your MLB Analytics Backend is ready!")
