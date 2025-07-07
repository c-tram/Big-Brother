"""
Management command to show a comprehensive summary of the loaded MLB data
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Max, Min
from apps.teams.models import League, Division, Venue, Team
from apps.players.models import Player, PlayerTeamHistory
from apps.games.models import Game


class Command(BaseCommand):
    help = 'Show a comprehensive summary of the loaded MLB data'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('='*60)
        )
        self.stdout.write(
            self.style.SUCCESS('MLB ANALYTICS BACKEND - DATA SUMMARY')
        )
        self.stdout.write(
            self.style.SUCCESS('='*60)
        )
        
        # Teams Data
        self.stdout.write("\n📊 TEAMS DATA:")
        self.stdout.write(f"  • Leagues: {League.objects.count()}")
        self.stdout.write(f"  • Divisions: {Division.objects.count()}")
        self.stdout.write(f"  • Venues: {Venue.objects.count()}")
        self.stdout.write(f"  • Teams: {Team.objects.count()}")
        
        # Show teams by division
        for division in Division.objects.all():
            team_count = Team.objects.filter(division=division).count()
            self.stdout.write(f"    - {division.name}: {team_count} teams")
        
        # Players Data
        self.stdout.write("\n👥 PLAYERS DATA:")
        self.stdout.write(f"  • Total Players: {Player.objects.count()}")
        self.stdout.write(f"  • Active Players: {Player.objects.filter(active=True).count()}")
        
        # Show players by team
        for team in Team.objects.all():
            player_count = Player.objects.filter(current_team=team).count()
            if player_count > 0:
                self.stdout.write(f"    - {team.abbreviation}: {player_count} players")
        
        # Show players by position
        positions = Player.objects.values('primary_position').annotate(count=Count('id')).order_by('-count')
        self.stdout.write(f"  • By Position:")
        for pos in positions:
            if pos['primary_position']:
                self.stdout.write(f"    - {pos['primary_position']}: {pos['count']} players")
        
        # Games Data
        self.stdout.write("\n⚾ GAMES DATA:")
        self.stdout.write(f"  • Total Games: {Game.objects.count()}")
        
        # Show games by date
        game_dates = Game.objects.values('game_date').annotate(count=Count('id')).order_by('game_date')
        self.stdout.write(f"  • By Date:")
        for date_info in game_dates:
            self.stdout.write(f"    - {date_info['game_date']}: {date_info['count']} games")
        
        # Show score statistics
        if Game.objects.count() > 0:
            avg_home_score = Game.objects.aggregate(Avg('home_score'))['home_score__avg']
            avg_away_score = Game.objects.aggregate(Avg('away_score'))['away_score__avg']
            max_score = max(
                Game.objects.aggregate(Max('home_score'))['home_score__max'] or 0,
                Game.objects.aggregate(Max('away_score'))['away_score__max'] or 0
            )
            
            self.stdout.write(f"  • Average Home Score: {avg_home_score:.1f}")
            self.stdout.write(f"  • Average Away Score: {avg_away_score:.1f}")
            self.stdout.write(f"  • Highest Score: {max_score}")
        
        # API Endpoints
        self.stdout.write("\n🔗 API ENDPOINTS:")
        self.stdout.write("  • Teams:")
        self.stdout.write("    - http://localhost:8000/api/v1/teams/")
        self.stdout.write("    - http://localhost:8000/api/v1/teams/teams/")
        self.stdout.write("    - http://localhost:8000/api/v1/teams/leagues/")
        self.stdout.write("    - http://localhost:8000/api/v1/teams/divisions/")
        self.stdout.write("    - http://localhost:8000/api/v1/teams/venues/")
        
        self.stdout.write("  • Players:")
        self.stdout.write("    - http://localhost:8000/api/v1/players/")
        self.stdout.write("    - http://localhost:8000/api/v1/players/players/")
        self.stdout.write("    - http://localhost:8000/api/v1/players/team-history/")
        
        self.stdout.write("  • Games:")
        self.stdout.write("    - http://localhost:8000/api/v1/games/")
        self.stdout.write("    - http://localhost:8000/api/v1/games/games/")
        self.stdout.write("    - http://localhost:8000/api/v1/games/events/")
        
        self.stdout.write("  • Analytics:")
        self.stdout.write("    - http://localhost:8000/api/v1/analytics/")
        self.stdout.write("    - http://localhost:8000/api/v1/analytics/player-analytics/")
        self.stdout.write("    - http://localhost:8000/api/v1/analytics/game-analytics/")
        
        # Sample API Calls
        self.stdout.write("\n🧪 SAMPLE API CALLS:")
        self.stdout.write("  • Get all teams:")
        self.stdout.write("    curl http://localhost:8000/api/v1/teams/teams/")
        
        self.stdout.write("  • Get Yankees players:")
        self.stdout.write("    curl 'http://localhost:8000/api/v1/players/players/?current_team__abbreviation=NYY'")
        
        self.stdout.write("  • Get games from 2024-04-01:")
        self.stdout.write("    curl 'http://localhost:8000/api/v1/games/games/?game_date=2024-04-01'")
        
        self.stdout.write("  • Search for players named 'Judge':")
        self.stdout.write("    curl 'http://localhost:8000/api/v1/players/players/?search=Judge'")
        
        self.stdout.write(
            self.style.SUCCESS('\n🚀 Your MLB Analytics Backend is fully operational!')
        )
        self.stdout.write(
            self.style.SUCCESS('='*60)
        )
