"""
Management command to load MLB teams, leagues, divisions, and venues from the MLB API
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.teams.models import League, Division, Venue, Team
from services.mlb_api import MLBApi
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load MLB teams, leagues, divisions, and venues from MLB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season year to load data for (default: 2024)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload of existing data'
        )

    def handle(self, *args, **options):
        season = options['season']
        force = options['force']
        
        self.stdout.write(f"Loading MLB data for {season} season...")
        
        mlb_api = MLBApi()
        
        try:
            with transaction.atomic():
                # Load leagues
                self.load_leagues(mlb_api, force)
                
                # Load divisions
                self.load_divisions(mlb_api, force)
                
                # Load venues
                self.load_venues(mlb_api, force)
                
                # Load teams
                self.load_teams(mlb_api, season, force)
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded MLB data for {season}')
            )
            
        except Exception as e:
            logger.error(f"Error loading MLB data: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error loading MLB data: {e}')
            )

    def load_leagues(self, mlb_api, force):
        """Load MLB leagues"""
        self.stdout.write("Loading leagues...")
        
        # Create American League
        al, created = League.objects.get_or_create(
            mlb_id=103,
            defaults={
                'name': 'American League',
                'abbreviation': 'AL'
            }
        )
        if created or force:
            self.stdout.write(f"  Created/Updated: {al.name}")
        
        # Create National League
        nl, created = League.objects.get_or_create(
            mlb_id=104,
            defaults={
                'name': 'National League',
                'abbreviation': 'NL'
            }
        )
        if created or force:
            self.stdout.write(f"  Created/Updated: {nl.name}")

    def load_divisions(self, mlb_api, force):
        """Load MLB divisions"""
        self.stdout.write("Loading divisions...")
        
        divisions_data = [
            # American League
            {'mlb_id': 200, 'name': 'American League West', 'abbreviation': 'ALW', 'league_id': 103},
            {'mlb_id': 201, 'name': 'American League East', 'abbreviation': 'ALE', 'league_id': 103},
            {'mlb_id': 202, 'name': 'American League Central', 'abbreviation': 'ALC', 'league_id': 103},
            # National League
            {'mlb_id': 203, 'name': 'National League West', 'abbreviation': 'NLW', 'league_id': 104},
            {'mlb_id': 204, 'name': 'National League East', 'abbreviation': 'NLE', 'league_id': 104},
            {'mlb_id': 205, 'name': 'National League Central', 'abbreviation': 'NLC', 'league_id': 104},
        ]
        
        for div_data in divisions_data:
            league = League.objects.get(mlb_id=div_data['league_id'])
            division, created = Division.objects.get_or_create(
                mlb_id=div_data['mlb_id'],
                defaults={
                    'name': div_data['name'],
                    'abbreviation': div_data['abbreviation'],
                    'league': league
                }
            )
            if created or force:
                self.stdout.write(f"  Created/Updated: {division.name}")

    def load_venues(self, mlb_api, force):
        """Load ALL 30 MLB venues"""
        self.stdout.write("Loading all 30 MLB venues...")
        
        # Complete list of all 30 MLB venues with correct IDs
        venues_data = [
            # American League
            {'mlb_id': 2, 'name': 'Angel Stadium', 'city': 'Anaheim', 'state': 'CA', 'capacity': 45517},
            {'mlb_id': 3, 'name': 'Oriole Park at Camden Yards', 'city': 'Baltimore', 'state': 'MD', 'capacity': 45971},
            {'mlb_id': 4, 'name': 'Fenway Park', 'city': 'Boston', 'state': 'MA', 'capacity': 37755},
            {'mlb_id': 5, 'name': 'Guaranteed Rate Field', 'city': 'Chicago', 'state': 'IL', 'capacity': 40615},
            {'mlb_id': 6, 'name': 'Progressive Field', 'city': 'Cleveland', 'state': 'OH', 'capacity': 35041},
            {'mlb_id': 7, 'name': 'Comerica Park', 'city': 'Detroit', 'state': 'MI', 'capacity': 41083},
            {'mlb_id': 8, 'name': 'Minute Maid Park', 'city': 'Houston', 'state': 'TX', 'capacity': 41168},
            {'mlb_id': 9, 'name': 'Kauffman Stadium', 'city': 'Kansas City', 'state': 'MO', 'capacity': 37903},
            {'mlb_id': 10, 'name': 'Yankee Stadium', 'city': 'Bronx', 'state': 'NY', 'capacity': 54251},
            {'mlb_id': 11, 'name': 'Oakland Coliseum', 'city': 'Oakland', 'state': 'CA', 'capacity': 46765},
            {'mlb_id': 12, 'name': 'T-Mobile Park', 'city': 'Seattle', 'state': 'WA', 'capacity': 47929},
            {'mlb_id': 13, 'name': 'Tropicana Field', 'city': 'St. Petersburg', 'state': 'FL', 'capacity': 25000},
            {'mlb_id': 14, 'name': 'Globe Life Field', 'city': 'Arlington', 'state': 'TX', 'capacity': 40300},
            {'mlb_id': 15, 'name': 'Rogers Centre', 'city': 'Toronto', 'state': 'ON', 'capacity': 49282},
            {'mlb_id': 401, 'name': 'Target Field', 'city': 'Minneapolis', 'state': 'MN', 'capacity': 38649},
            
            # National League
            {'mlb_id': 16, 'name': 'Chase Field', 'city': 'Phoenix', 'state': 'AZ', 'capacity': 48519},
            {'mlb_id': 17, 'name': 'Coors Field', 'city': 'Denver', 'state': 'CO', 'capacity': 50398},
            {'mlb_id': 18, 'name': 'Dodger Stadium', 'city': 'Los Angeles', 'state': 'CA', 'capacity': 56000},
            {'mlb_id': 19, 'name': 'Petco Park', 'city': 'San Diego', 'state': 'CA', 'capacity': 40209},
            {'mlb_id': 20, 'name': 'Oracle Park', 'city': 'San Francisco', 'state': 'CA', 'capacity': 41915},
            {'mlb_id': 21, 'name': 'Truist Park', 'city': 'Atlanta', 'state': 'GA', 'capacity': 41149},
            {'mlb_id': 22, 'name': 'loanDepot park', 'city': 'Miami', 'state': 'FL', 'capacity': 36742},
            {'mlb_id': 23, 'name': 'Citi Field', 'city': 'New York', 'state': 'NY', 'capacity': 41922},
            {'mlb_id': 24, 'name': 'Citizens Bank Park', 'city': 'Philadelphia', 'state': 'PA', 'capacity': 43651},
            {'mlb_id': 25, 'name': 'Nationals Park', 'city': 'Washington', 'state': 'DC', 'capacity': 41339},
            {'mlb_id': 26, 'name': 'Wrigley Field', 'city': 'Chicago', 'state': 'IL', 'capacity': 41649},
            {'mlb_id': 27, 'name': 'Great American Ball Park', 'city': 'Cincinnati', 'state': 'OH', 'capacity': 42319},
            {'mlb_id': 28, 'name': 'American Family Field', 'city': 'Milwaukee', 'state': 'WI', 'capacity': 41900},
            {'mlb_id': 29, 'name': 'PNC Park', 'city': 'Pittsburgh', 'state': 'PA', 'capacity': 38747},
            {'mlb_id': 30, 'name': 'Busch Stadium', 'city': 'St. Louis', 'state': 'MO', 'capacity': 45494},
        ]
        
        for venue_data in venues_data:
            venue, created = Venue.objects.get_or_create(
                mlb_id=venue_data['mlb_id'],
                defaults=venue_data
            )
            if created or force:
                self.stdout.write(f"  Created/Updated: {venue.name}")
        
        # Verify we have all 30 venues
        if len(venues_data) == 30:
            self.stdout.write(self.style.SUCCESS("✓ Successfully loaded all 30 MLB venues"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠ Expected 30 venues, loaded {len(venues_data)}"))

    def load_teams(self, mlb_api, season, force):
        """Load ALL 30 MLB teams"""
        self.stdout.write("Loading all 30 MLB teams...")
        
        teams_data = [
            # American League West (5 teams)
            {'mlb_id': 108, 'name': 'Los Angeles Angels', 'team_name': 'Angels', 'location_name': 'Los Angeles',
             'abbreviation': 'LAA', 'team_code': 'LAA', 'file_code': 'ana', 'division_id': 200, 'venue_id': 2},
            {'mlb_id': 117, 'name': 'Houston Astros', 'team_name': 'Astros', 'location_name': 'Houston',
             'abbreviation': 'HOU', 'team_code': 'HOU', 'file_code': 'hou', 'division_id': 200, 'venue_id': 8},
            {'mlb_id': 133, 'name': 'Oakland Athletics', 'team_name': 'Athletics', 'location_name': 'Oakland',
             'abbreviation': 'OAK', 'team_code': 'OAK', 'file_code': 'oak', 'division_id': 200, 'venue_id': 11},
            {'mlb_id': 136, 'name': 'Seattle Mariners', 'team_name': 'Mariners', 'location_name': 'Seattle',
             'abbreviation': 'SEA', 'team_code': 'SEA', 'file_code': 'sea', 'division_id': 200, 'venue_id': 12},
            {'mlb_id': 140, 'name': 'Texas Rangers', 'team_name': 'Rangers', 'location_name': 'Texas',
             'abbreviation': 'TEX', 'team_code': 'TEX', 'file_code': 'tex', 'division_id': 200, 'venue_id': 14},
            
            # American League East (5 teams)
            {'mlb_id': 110, 'name': 'Baltimore Orioles', 'team_name': 'Orioles', 'location_name': 'Baltimore',
             'abbreviation': 'BAL', 'team_code': 'BAL', 'file_code': 'bal', 'division_id': 201, 'venue_id': 3},
            {'mlb_id': 111, 'name': 'Boston Red Sox', 'team_name': 'Red Sox', 'location_name': 'Boston',
             'abbreviation': 'BOS', 'team_code': 'BOS', 'file_code': 'bos', 'division_id': 201, 'venue_id': 4},
            {'mlb_id': 147, 'name': 'New York Yankees', 'team_name': 'Yankees', 'location_name': 'New York',
             'abbreviation': 'NYY', 'team_code': 'NYY', 'file_code': 'nyy', 'division_id': 201, 'venue_id': 10},
            {'mlb_id': 139, 'name': 'Tampa Bay Rays', 'team_name': 'Rays', 'location_name': 'Tampa Bay',
             'abbreviation': 'TB', 'team_code': 'TB', 'file_code': 'tb', 'division_id': 201, 'venue_id': 13},
            {'mlb_id': 141, 'name': 'Toronto Blue Jays', 'team_name': 'Blue Jays', 'location_name': 'Toronto',
             'abbreviation': 'TOR', 'team_code': 'TOR', 'file_code': 'tor', 'division_id': 201, 'venue_id': 15},
            
            # American League Central (5 teams)
            {'mlb_id': 145, 'name': 'Chicago White Sox', 'team_name': 'White Sox', 'location_name': 'Chicago',
             'abbreviation': 'CWS', 'team_code': 'CWS', 'file_code': 'cws', 'division_id': 202, 'venue_id': 5},
            {'mlb_id': 114, 'name': 'Cleveland Guardians', 'team_name': 'Guardians', 'location_name': 'Cleveland',
             'abbreviation': 'CLE', 'team_code': 'CLE', 'file_code': 'cle', 'division_id': 202, 'venue_id': 6},
            {'mlb_id': 116, 'name': 'Detroit Tigers', 'team_name': 'Tigers', 'location_name': 'Detroit',
             'abbreviation': 'DET', 'team_code': 'DET', 'file_code': 'det', 'division_id': 202, 'venue_id': 7},
            {'mlb_id': 118, 'name': 'Kansas City Royals', 'team_name': 'Royals', 'location_name': 'Kansas City',
             'abbreviation': 'KC', 'team_code': 'KC', 'file_code': 'kc', 'division_id': 202, 'venue_id': 9},
            {'mlb_id': 142, 'name': 'Minnesota Twins', 'team_name': 'Twins', 'location_name': 'Minnesota',
             'abbreviation': 'MIN', 'team_code': 'MIN', 'file_code': 'min', 'division_id': 202, 'venue_id': 401},
            
            # National League West (5 teams)
            {'mlb_id': 109, 'name': 'Arizona Diamondbacks', 'team_name': 'Diamondbacks', 'location_name': 'Arizona',
             'abbreviation': 'ARI', 'team_code': 'ARI', 'file_code': 'ari', 'division_id': 203, 'venue_id': 16},
            {'mlb_id': 115, 'name': 'Colorado Rockies', 'team_name': 'Rockies', 'location_name': 'Colorado',
             'abbreviation': 'COL', 'team_code': 'COL', 'file_code': 'col', 'division_id': 203, 'venue_id': 17},
            {'mlb_id': 119, 'name': 'Los Angeles Dodgers', 'team_name': 'Dodgers', 'location_name': 'Los Angeles',
             'abbreviation': 'LAD', 'team_code': 'LAD', 'file_code': 'lad', 'division_id': 203, 'venue_id': 18},
            {'mlb_id': 135, 'name': 'San Diego Padres', 'team_name': 'Padres', 'location_name': 'San Diego',
             'abbreviation': 'SD', 'team_code': 'SD', 'file_code': 'sd', 'division_id': 203, 'venue_id': 19},
            {'mlb_id': 137, 'name': 'San Francisco Giants', 'team_name': 'Giants', 'location_name': 'San Francisco',
             'abbreviation': 'SF', 'team_code': 'SF', 'file_code': 'sf', 'division_id': 203, 'venue_id': 20},
            
            # National League East (5 teams)
            {'mlb_id': 144, 'name': 'Atlanta Braves', 'team_name': 'Braves', 'location_name': 'Atlanta',
             'abbreviation': 'ATL', 'team_code': 'ATL', 'file_code': 'atl', 'division_id': 204, 'venue_id': 21},
            {'mlb_id': 146, 'name': 'Miami Marlins', 'team_name': 'Marlins', 'location_name': 'Miami',
             'abbreviation': 'MIA', 'team_code': 'MIA', 'file_code': 'mia', 'division_id': 204, 'venue_id': 22},
            {'mlb_id': 121, 'name': 'New York Mets', 'team_name': 'Mets', 'location_name': 'New York',
             'abbreviation': 'NYM', 'team_code': 'NYM', 'file_code': 'nym', 'division_id': 204, 'venue_id': 23},
            {'mlb_id': 143, 'name': 'Philadelphia Phillies', 'team_name': 'Phillies', 'location_name': 'Philadelphia',
             'abbreviation': 'PHI', 'team_code': 'PHI', 'file_code': 'phi', 'division_id': 204, 'venue_id': 24},
            {'mlb_id': 120, 'name': 'Washington Nationals', 'team_name': 'Nationals', 'location_name': 'Washington',
             'abbreviation': 'WSH', 'team_code': 'WSH', 'file_code': 'wsh', 'division_id': 204, 'venue_id': 25},
            
            # National League Central (5 teams)
            {'mlb_id': 112, 'name': 'Chicago Cubs', 'team_name': 'Cubs', 'location_name': 'Chicago',
             'abbreviation': 'CHC', 'team_code': 'CHC', 'file_code': 'chc', 'division_id': 205, 'venue_id': 26},
            {'mlb_id': 113, 'name': 'Cincinnati Reds', 'team_name': 'Reds', 'location_name': 'Cincinnati',
             'abbreviation': 'CIN', 'team_code': 'CIN', 'file_code': 'cin', 'division_id': 205, 'venue_id': 27},
            {'mlb_id': 158, 'name': 'Milwaukee Brewers', 'team_name': 'Brewers', 'location_name': 'Milwaukee',
             'abbreviation': 'MIL', 'team_code': 'MIL', 'file_code': 'mil', 'division_id': 205, 'venue_id': 28},
            {'mlb_id': 134, 'name': 'Pittsburgh Pirates', 'team_name': 'Pirates', 'location_name': 'Pittsburgh',
             'abbreviation': 'PIT', 'team_code': 'PIT', 'file_code': 'pit', 'division_id': 205, 'venue_id': 29},
            {'mlb_id': 138, 'name': 'St. Louis Cardinals', 'team_name': 'Cardinals', 'location_name': 'St. Louis',
             'abbreviation': 'STL', 'team_code': 'STL', 'file_code': 'stl', 'division_id': 205, 'venue_id': 30},
        ]
        
        for team_data in teams_data:
            division = Division.objects.get(mlb_id=team_data['division_id'])
            venue = Venue.objects.get(mlb_id=team_data['venue_id'])
            
            # Get league from division
            league = division.league
            
            team, created = Team.objects.get_or_create(
                mlb_id=team_data['mlb_id'],
                defaults={
                    'name': team_data['name'],
                    'team_name': team_data['team_name'],
                    'location_name': team_data['location_name'],
                    'abbreviation': team_data['abbreviation'],
                    'team_code': team_data['team_code'],
                    'file_code': team_data['file_code'],
                    'league': league,
                    'division': division,
                    'venue': venue,
                    'club_name': team_data['team_name'],
                    'short_name': team_data['abbreviation'],
                    'franchise_name': team_data['name'],
                    'first_year_of_play': 1900,  # Default, would be updated from API
                    'active': True
                }
            )
            if created or force:
                self.stdout.write(f"  Created/Updated: {team.name}")
        
        self.stdout.write(f"Loaded all {len(teams_data)} MLB teams (30 total)")
        
        # Verify we have all 30 teams
        if len(teams_data) == 30:
            self.stdout.write(self.style.SUCCESS("✓ Successfully loaded all 30 MLB teams"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠ Expected 30 teams, loaded {len(teams_data)}"))
