"""
Management command to load sample MLB players from the MLB API
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.teams.models import Team
from apps.players.models import Player, PlayerTeamHistory
from services.mlb_api import MLBApi
import logging
from datetime import date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load sample MLB players from MLB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season year to load data for (default: 2024)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit number of players to load (default: 50)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload of existing data'
        )

    def handle(self, *args, **options):
        season = options['season']
        limit = options['limit']
        force = options['force']
        
        self.stdout.write(f"Loading {limit} MLB players for {season} season...")
        
        try:
            with transaction.atomic():
                self.load_sample_players(season, limit, force)
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded {limit} MLB players for {season}')
            )
            
        except Exception as e:
            logger.error(f"Error loading MLB players: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error loading MLB players: {e}')
            )

    def load_sample_players(self, season, limit, force):
        """Load sample MLB players"""
        self.stdout.write("Loading sample players...")
        
        # Sample player data (would typically come from MLB API)
        sample_players = [
            # Yankees
            {'mlb_id': 592450, 'first_name': 'Aaron', 'last_name': 'Judge', 'position': 'OF', 
             'jersey_number': 99, 'birth_date': '1992-04-26', 'bats': 'R', 'throws': 'R', 
             'height': 79, 'weight': 282, 'team_abbrev': 'NYY'},
            {'mlb_id': 596059, 'first_name': 'Gleyber', 'last_name': 'Torres', 'position': '2B', 
             'jersey_number': 25, 'birth_date': '1996-12-13', 'bats': 'R', 'throws': 'R', 
             'height': 73, 'weight': 205, 'team_abbrev': 'NYY'},
            
            # Red Sox
            {'mlb_id': 646240, 'first_name': 'Rafael', 'last_name': 'Devers', 'position': '3B', 
             'jersey_number': 11, 'birth_date': '1996-10-24', 'bats': 'L', 'throws': 'R', 
             'height': 72, 'weight': 240, 'team_abbrev': 'BOS'},
            {'mlb_id': 650556, 'first_name': 'Alex', 'last_name': 'Verdugo', 'position': 'OF', 
             'jersey_number': 16, 'birth_date': '1996-05-15', 'bats': 'L', 'throws': 'L', 
             'height': 72, 'weight': 192, 'team_abbrev': 'BOS'},
            
            # Astros
            {'mlb_id': 514888, 'first_name': 'Jose', 'last_name': 'Altuve', 'position': '2B', 
             'jersey_number': 27, 'birth_date': '1990-05-06', 'bats': 'R', 'throws': 'R', 
             'height': 66, 'weight': 166, 'team_abbrev': 'HOU'},
            {'mlb_id': 608324, 'first_name': 'Alex', 'last_name': 'Bregman', 'position': '3B', 
             'jersey_number': 2, 'birth_date': '1994-03-30', 'bats': 'R', 'throws': 'R', 
             'height': 72, 'weight': 180, 'team_abbrev': 'HOU'},
            
            # Angels
            {'mlb_id': 545361, 'first_name': 'Mike', 'last_name': 'Trout', 'position': 'OF', 
             'jersey_number': 27, 'birth_date': '1991-08-07', 'bats': 'R', 'throws': 'R', 
             'height': 73, 'weight': 235, 'team_abbrev': 'LAA'},
            {'mlb_id': 660271, 'first_name': 'Shohei', 'last_name': 'Ohtani', 'position': 'DH', 
             'jersey_number': 17, 'birth_date': '1994-07-05', 'bats': 'L', 'throws': 'R', 
             'height': 76, 'weight': 210, 'team_abbrev': 'LAA'},
            
            # Orioles
            {'mlb_id': 663993, 'first_name': 'Adley', 'last_name': 'Rutschman', 'position': 'C', 
             'jersey_number': 35, 'birth_date': '1998-02-06', 'bats': 'S', 'throws': 'R', 
             'height': 74, 'weight': 220, 'team_abbrev': 'BAL'},
            {'mlb_id': 668804, 'first_name': 'Gunnar', 'last_name': 'Henderson', 'position': 'SS', 
             'jersey_number': 2, 'birth_date': '2001-06-29', 'bats': 'L', 'throws': 'R', 
             'height': 75, 'weight': 210, 'team_abbrev': 'BAL'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for player_data in sample_players[:limit]:
            try:
                # Get the team
                team = Team.objects.get(abbreviation=player_data['team_abbrev'])
                
                # Parse birth date
                birth_date = date.fromisoformat(player_data['birth_date'])
                
                # Create or update player
                player, created = Player.objects.get_or_create(
                    mlb_id=player_data['mlb_id'],
                    defaults={
                        'first_name': player_data['first_name'],
                        'last_name': player_data['last_name'],
                        'full_name': f"{player_data['first_name']} {player_data['last_name']}",
                        'birth_date': birth_date,
                        'birth_city': 'Unknown',  # Would be filled from API
                        'birth_state_province': 'Unknown',  # Would be filled from API
                        'birth_country': 'USA',  # Default
                        'height': f"{player_data['height'] // 12}' {player_data['height'] % 12}\"",  # Convert inches to feet/inches
                        'weight': player_data['weight'],
                        'bat_side': player_data['bats'],
                        'pitch_hand': player_data['throws'],
                        'primary_position': player_data['position'],
                        'current_team': team,
                        'active': True,
                        'mlb_debut_date': date(2015, 1, 1),  # Default
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"  Created: {player.full_name} ({team.abbreviation})")
                elif force:
                    # Update existing player
                    player.current_team = team
                    player.save()
                    updated_count += 1
                    self.stdout.write(f"  Updated: {player.full_name} ({team.abbreviation})")
                
                # Create team history entry
                history, hist_created = PlayerTeamHistory.objects.get_or_create(
                    player=player,
                    team=team,
                    start_date=date(season, 3, 1),  # Spring training
                    defaults={
                        'transaction_type': 'free_agent',
                    }
                )
                
            except Team.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Team {player_data['team_abbrev']} not found for player {player_data['first_name']} {player_data['last_name']}")
                )
                continue
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating player {player_data['first_name']} {player_data['last_name']}: {e}")
                )
                continue
        
        self.stdout.write(f"Created {created_count} players, updated {updated_count} players")
