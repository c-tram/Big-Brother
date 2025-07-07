"""
Comprehensive MLB data sync using the enhanced API service
This command demonstrates the full power of our complete MLB API coverage
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.teams.models import Team, Venue
from apps.players.models import Player
from apps.games.models import Game, GamePlayerStats
from services.enhanced_mlb_api_fixed import EnhancedMLBApi, MLBApiError
from datetime import datetime, timedelta
import json

class Command(BaseCommand):
    help = 'Comprehensive MLB data sync using enhanced API coverage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo-query',
            choices=['aaron-judge-dodgers', 'player-profile', 'league-leaders', 'transactions'],
            help='Run specific demonstration query'
        )
        parser.add_argument(
            '--player-name',
            type=str,
            help='Player name for queries'
        )
        parser.add_argument(
            '--venue-name', 
            type=str,
            help='Venue name for queries'
        )
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season year'
        )

    def handle(self, *args, **options):
        demo_query = options.get('demo_query')
        player_name = options.get('player_name', 'Aaron Judge')
        venue_name = options.get('venue_name', 'Dodger Stadium')
        season = options['season']

        self.stdout.write("🚀 Starting Comprehensive MLB Data Sync...")
        
        enhanced_api = EnhancedMLBApi()
        
        try:
            if demo_query == 'aaron-judge-dodgers':
                self.demo_aaron_judge_dodgers(enhanced_api, player_name, venue_name, [season])
            elif demo_query == 'player-profile':
                self.demo_comprehensive_player_profile(enhanced_api, player_name)
            elif demo_query == 'league-leaders':
                self.demo_league_leaders(enhanced_api, season)
            elif demo_query == 'transactions':
                self.demo_transactions(enhanced_api)
            else:
                self.demo_all_capabilities(enhanced_api, player_name, venue_name, season)
                
        except MLBApiError as e:
            self.stdout.write(self.style.ERROR(f"MLB API Error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))

    def demo_aaron_judge_dodgers(self, api, player_name, venue_name, seasons):
        """Demonstrate comprehensive player venue performance analysis"""
        self.stdout.write(f"\n🎯 DEMO: {player_name} Performance at {venue_name}")
        self.stdout.write("=" * 60)
        
        result = api.get_player_venue_performance(player_name, venue_name, seasons)
        
        if 'error' in result:
            self.stdout.write(self.style.ERROR(f"Error: {result['error']}"))
            return
        
        # Display results
        player = result['player']
        self.stdout.write(f"🏟️  Player: {player['name']} (ID: {player['id']})")
        self.stdout.write(f"🏟️  Team: {player['team']}")
        self.stdout.write(f"🏟️  Venue: {result['venue']}")
        self.stdout.write(f"🏟️  Seasons Analyzed: {result['seasons']}")
        self.stdout.write(f"🏟️  Games Found: {result['games_found']}")
        
        # Career stats
        if result.get('career_stats', {}).get('hitting'):
            hitting = result['career_stats']['hitting']
            self.stdout.write(f"\n📊 Career Hitting Stats:")
            self.stdout.write(f"   • Games: {hitting.get('g', 'N/A')}")
            self.stdout.write(f"   • Batting Average: {hitting.get('avg', 'N/A')}")
            self.stdout.write(f"   • Home Runs: {hitting.get('hr', 'N/A')}")
            self.stdout.write(f"   • RBIs: {hitting.get('rbi', 'N/A')}")
            self.stdout.write(f"   • OPS: {hitting.get('ops', 'N/A')}")
        
        # Season stats
        for season, stats in result.get('season_stats', {}).items():
            if stats:
                self.stdout.write(f"\n📊 {season} Season Stats:")
                self.stdout.write(f"   • Games: {stats.get('g', 'N/A')}")
                self.stdout.write(f"   • Batting Average: {stats.get('avg', 'N/A')}")
                self.stdout.write(f"   • Home Runs: {stats.get('hr', 'N/A')}")
                self.stdout.write(f"   • RBIs: {stats.get('rbi', 'N/A')}")
        
        # Sample games
        if result.get('games'):
            self.stdout.write(f"\n🎮 Sample Games at {venue_name}:")
            for game in result['games'][:5]:
                self.stdout.write(f"   • {game['date']} - Game ID: {game['game_id']}")

    def demo_comprehensive_player_profile(self, api, player_name):
        """Demonstrate comprehensive player profile analysis"""
        self.stdout.write(f"\n👤 DEMO: Comprehensive Profile for {player_name}")
        self.stdout.write("=" * 60)
        
        profile = api.get_comprehensive_player_profile(player_name)
        
        if 'error' in profile:
            self.stdout.write(self.style.ERROR(f"Error: {profile['error']}"))
            return
        
        # Basic info
        basic = profile.get('basic_info', {})
        self.stdout.write(f"📋 Basic Information:")
        self.stdout.write(f"   • Name: {basic.get('name_display_first_last', 'N/A')}")
        self.stdout.write(f"   • Position: {basic.get('position', 'N/A')}")
        self.stdout.write(f"   • Team: {basic.get('team_full', 'N/A')}")
        self.stdout.write(f"   • Bats/Throws: {basic.get('bats', 'N/A')}/{basic.get('throws', 'N/A')}")
        
        # Detailed info
        detailed = profile.get('detailed_info', {})
        if detailed:
            self.stdout.write(f"\n📝 Detailed Information:")
            self.stdout.write(f"   • Birth Date: {detailed.get('birth_date', 'N/A')}")
            self.stdout.write(f"   • Height/Weight: {detailed.get('height_feet', 'N/A')}'{detailed.get('height_inches', 'N/A')}\" / {detailed.get('weight', 'N/A')} lbs")
            self.stdout.write(f"   • Pro Debut: {detailed.get('pro_debut_date', 'N/A')}")
            self.stdout.write(f"   • College: {detailed.get('college', 'N/A')}")
        
        # Team history
        team_history = profile.get('team_history', [])
        if team_history:
            if not isinstance(team_history, list):
                team_history = [team_history]
            
            self.stdout.write(f"\n🏟️  Team History:")
            for i, team in enumerate(team_history[:5]):  # Show last 5 teams
                self.stdout.write(f"   • {team.get('season', 'N/A')}: {team.get('team', 'N/A')} ({team.get('league', 'N/A')})")
        
        # Career stats
        career_hitting = profile.get('career_stats', {}).get('hitting', {})
        if career_hitting:
            self.stdout.write(f"\n🏏 Career Hitting Stats:")
            self.stdout.write(f"   • Games: {career_hitting.get('g', 'N/A')}")
            self.stdout.write(f"   • At Bats: {career_hitting.get('ab', 'N/A')}")
            self.stdout.write(f"   • Hits: {career_hitting.get('h', 'N/A')}")
            self.stdout.write(f"   • Batting Average: {career_hitting.get('avg', 'N/A')}")
            self.stdout.write(f"   • Home Runs: {career_hitting.get('hr', 'N/A')}")
            self.stdout.write(f"   • RBIs: {career_hitting.get('rbi', 'N/A')}")
            self.stdout.write(f"   • OPS: {career_hitting.get('ops', 'N/A')}")
        
        # Current season
        current_hitting = profile.get('current_season_stats', {}).get('hitting', {})
        if current_hitting:
            self.stdout.write(f"\n📊 Current Season Hitting:")
            self.stdout.write(f"   • Games: {current_hitting.get('g', 'N/A')}")
            self.stdout.write(f"   • Batting Average: {current_hitting.get('avg', 'N/A')}")
            self.stdout.write(f"   • Home Runs: {current_hitting.get('hr', 'N/A')}")
            self.stdout.write(f"   • RBIs: {current_hitting.get('rbi', 'N/A')}")

    def demo_league_leaders(self, api, season):
        """Demonstrate league leaders functionality"""
        self.stdout.write(f"\n🏆 DEMO: League Leaders for {season}")
        self.stdout.write("=" * 60)
        
        # Hitting leaders
        try:
            hitting_leaders = api.get_hitting_leaders('hr', season, limit=5, 
                                                     include_fields=['name_display_first_last', 'hr'])
            
            self.stdout.write(f"🏏 Home Run Leaders ({season}):")
            leaders_data = hitting_leaders.get('leader_hitting_repeater', {}).get('leader_hitting_mux', {}).get('queryResults', {}).get('row', [])
            
            if leaders_data:
                for i, leader in enumerate(leaders_data, 1):
                    name = leader.get('name_display_first_last', 'Unknown')
                    hrs = leader.get('hr', 'N/A')
                    self.stdout.write(f"   {i}. {name}: {hrs} HR")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not get hitting leaders: {e}"))
        
        # Pitching leaders
        try:
            pitching_leaders = api.get_pitching_leaders('era', season, limit=5,
                                                       include_fields=['name_display_first_last', 'era'])
            
            self.stdout.write(f"\n⚾ ERA Leaders ({season}):")
            leaders_data = pitching_leaders.get('leader_pitching_repeater', {}).get('leader_pitching_mux', {}).get('queryResults', {}).get('row', [])
            
            if leaders_data:
                for i, leader in enumerate(leaders_data, 1):
                    name = leader.get('name_display_first_last', 'Unknown')
                    era = leader.get('era', 'N/A')
                    self.stdout.write(f"   {i}. {name}: {era} ERA")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not get pitching leaders: {e}"))

    def demo_transactions(self, api):
        """Demonstrate transactions functionality"""
        self.stdout.write(f"\n💼 DEMO: Recent Transactions")
        self.stdout.write("=" * 60)
        
        # Get transactions from last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        try:
            transactions = api.get_transactions(
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
            
            trans_data = transactions.get('transaction_all', {}).get('queryResults', {}).get('row', [])
            
            if trans_data:
                if not isinstance(trans_data, list):
                    trans_data = [trans_data]
                
                self.stdout.write(f"Recent Transactions (Last 30 days):")
                for trans in trans_data[:10]:  # Show first 10
                    player = trans.get('player', 'Unknown Player')
                    trans_type = trans.get('type', 'Unknown')
                    team = trans.get('team', 'Unknown Team')
                    date = trans.get('trans_date', 'Unknown Date')
                    self.stdout.write(f"   • {date[:10]}: {player} - {trans_type} ({team})")
            else:
                self.stdout.write("No recent transactions found.")
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not get transactions: {e}"))

    def demo_all_capabilities(self, api, player_name, venue_name, season):
        """Run all demonstration capabilities"""
        self.stdout.write("🎪 RUNNING ALL ENHANCED API DEMONSTRATIONS")
        self.stdout.write("=" * 80)
        
        self.demo_aaron_judge_dodgers(api, player_name, venue_name, [season])
        self.demo_comprehensive_player_profile(api, player_name)
        self.demo_league_leaders(api, season)
        self.demo_transactions(api)
        
        # Additional capabilities demo
        self.stdout.write(f"\n🔧 ADDITIONAL CAPABILITIES AVAILABLE:")
        self.stdout.write("   • Player search by partial name")
        self.stdout.write("   • Complete team rosters (40-man, all-time)")
        self.stdout.write("   • Season and career statistics")
        self.stdout.write("   • League-specific performance splits")
        self.stdout.write("   • Projected statistics")
        self.stdout.write("   • Injury reports")
        self.stdout.write("   • Broadcast information")
        self.stdout.write("   • Game type information")
        self.stdout.write("   • Historical transactions")
        
        self.stdout.write(f"\n✅ COMPREHENSIVE MLB API COVERAGE DEMONSTRATED!")
        self.stdout.write("🎯 Your backend now supports flexible querying for frontend LLM integration!")
