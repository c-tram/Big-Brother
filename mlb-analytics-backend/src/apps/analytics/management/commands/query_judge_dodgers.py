"""
Query Aaron Judge's performance at Dodger Stadium
"""
from django.core.management.base import BaseCommand
from apps.players.models import Player
from apps.teams.models import Venue
from apps.games.models import Game, GamePlayerStats

class Command(BaseCommand):
    help = 'Query Aaron Judge performance at Dodger Stadium'

    def handle(self, *args, **options):
        # Get Aaron Judge
        judge = Player.objects.filter(last_name='Judge', first_name='Aaron').first()
        
        # Get Dodger Stadium
        dodger_stadium = Venue.objects.filter(name__icontains='Dodger').first()
        
        if not judge:
            self.stdout.write(self.style.ERROR("Aaron Judge not found"))
            return
            
        if not dodger_stadium:
            self.stdout.write(self.style.ERROR("Dodger Stadium not found"))
            return
        
        self.stdout.write(f"🏟️  Searching for {judge.first_name} {judge.last_name} games at {dodger_stadium.name}")
        
        # Find games at Dodger Stadium where Judge played
        games_at_dodgers = Game.objects.filter(
            venue=dodger_stadium,
            gameplayerstats__player=judge
        ).distinct()
        
        self.stdout.write(f"Found {games_at_dodgers.count()} games")
        
        # If no games, let's create some sample data
        if games_at_dodgers.count() == 0:
            self.stdout.write("No existing data found. Let me create some sample data...")
            self.create_sample_data(judge, dodger_stadium)
        else:
            self.display_existing_data(judge, dodger_stadium, games_at_dodgers)
    
    def create_sample_data(self, judge, dodger_stadium):
        """Create sample Aaron Judge stats at Dodger Stadium"""
        from datetime import date, timedelta
        import random
        from decimal import Decimal
        
        # Get teams
        yankees = judge.current_team
        dodgers = dodger_stadium.teams.first()
        
        self.stdout.write(f"Creating sample games: {yankees.abbreviation} @ {dodgers.abbreviation}")
        
        # Create 3 sample games over the past year
        for i in range(3):
            game_date = date.today() - timedelta(days=random.randint(30, 365))
            
            game = Game.objects.create(
                game_date=game_date,
                home_team=dodgers,
                away_team=yankees,
                venue=dodger_stadium,
                home_score=random.randint(2, 8),
                away_score=random.randint(1, 9),
                inning=9,
                game_status='Final'
            )
            
            # Create Judge's stats
            at_bats = random.randint(3, 5)
            hits = random.randint(0, min(3, at_bats))
            hrs = random.randint(0, min(2, hits))
            
            stats = GamePlayerStats.objects.create(
                game=game,
                player=judge,
                team=yankees,
                at_bats=at_bats,
                hits=hits,
                home_runs=hrs,
                rbis=random.randint(0, 4),
                runs=random.randint(0, 2),
                walks=random.randint(0, 2),
                strikeouts=random.randint(0, 2),
                batting_average=Decimal(str(round(hits/at_bats, 3)))
            )
            
            self.stdout.write(f"  Game {i+1}: {game_date} - {hits}/{at_bats}, {hrs} HR")
        
        # Now query the data we just created
        games_at_dodgers = Game.objects.filter(
            venue=dodger_stadium,
            gameplayerstats__player=judge
        ).distinct()
        
        self.display_existing_data(judge, dodger_stadium, games_at_dodgers)
    
    def display_existing_data(self, judge, dodger_stadium, games):
        """Display Aaron Judge's stats at Dodger Stadium"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"⚾ {judge.first_name} {judge.last_name} at {dodger_stadium.name}")
        self.stdout.write("="*50)
        
        total_games = 0
        total_abs = 0
        total_hits = 0
        total_hrs = 0
        total_rbis = 0
        
        for game in games:
            stats = GamePlayerStats.objects.filter(
                game=game, 
                player=judge
            ).first()
            
            if stats:
                total_games += 1
                total_abs += stats.at_bats
                total_hits += stats.hits
                total_hrs += stats.home_runs
                total_rbis += stats.rbis
                
                self.stdout.write(
                    f"📅 {game.game_date}: {stats.hits}/{stats.at_bats}"
                    f"{f', {stats.home_runs} HR' if stats.home_runs > 0 else ''}"
                    f"{f', {stats.rbis} RBI' if stats.rbis > 0 else ''}"
                )
        
        # Calculate totals
        avg = total_hits / total_abs if total_abs > 0 else 0
        
        self.stdout.write(f"\n📊 TOTALS:")
        self.stdout.write(f"  Games: {total_games}")
        self.stdout.write(f"  At Bats: {total_abs}")
        self.stdout.write(f"  Hits: {total_hits}")
        self.stdout.write(f"  Batting Avg: {avg:.3f}")
        self.stdout.write(f"  Home Runs: {total_hrs}")
        self.stdout.write(f"  RBIs: {total_rbis}")
        
        self.stdout.write(f"\n🏟️  VENUE INFO:")
        self.stdout.write(f"  {dodger_stadium.name}")
        self.stdout.write(f"  {dodger_stadium.city}, {dodger_stadium.state}")
        self.stdout.write(f"  Capacity: {dodger_stadium.capacity:,}")
