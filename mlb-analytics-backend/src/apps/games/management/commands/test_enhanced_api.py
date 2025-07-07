"""
Enhanced MLB API Test Command - Phase 1 Implementation
Demonstrates comprehensive MLB data coverage for frontend LLM integration
"""
from django.core.management.base import BaseCommand
from services.enhanced_mlb_api_v2 import EnhancedMLBApiV2, MLBApiError
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Test Enhanced MLB API with comprehensive data coverage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            choices=['aaron-judge', 'player-search', 'league-leaders', 'all'],
            default='aaron-judge',
            help='Which test to run'
        )
        parser.add_argument(
            '--player',
            type=str,
            default='Aaron Judge',
            help='Player name to search for'
        )
        parser.add_argument(
            '--venue',
            type=str,
            default='Dodger Stadium',
            help='Venue name for analysis'
        )
        parser.add_argument(
            '--season',
            type=int,
            default=2024,
            help='Season for analysis'
        )

    def handle(self, *args, **options):
        test_type = options['test']
        player_name = options['player']
        venue_name = options['venue']
        season = options['season']

        self.stdout.write("🚀 ENHANCED MLB API - PHASE 1 IMPLEMENTATION TEST")
        self.stdout.write("=" * 70)
        
        api = EnhancedMLBApiV2()
        
        try:
            if test_type == 'aaron-judge' or test_type == 'all':
                self.test_aaron_judge_dodgers(api, player_name, venue_name, season)
            
            if test_type == 'player-search' or test_type == 'all':
                self.test_player_search(api, player_name)
            
            if test_type == 'league-leaders' or test_type == 'all':
                self.test_league_leaders(api, season)
                
        except MLBApiError as e:
            self.stdout.write(self.style.ERROR(f"MLB API Error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            import traceback
            traceback.print_exc()

    def test_aaron_judge_dodgers(self, api, player_name, venue_name, season):
        """Test the key use case: Aaron Judge at Dodger Stadium"""
        self.stdout.write(f"\n🎯 TEST: {player_name} Performance at {venue_name}")
        self.stdout.write("=" * 60)
        
        # Test venue-specific performance analysis
        result = api.get_player_venue_performance(player_name, venue_name, [season])
        
        if 'error' in result:
            self.stdout.write(self.style.ERROR(f"❌ Error: {result['error']}"))
            return
        
        # Display comprehensive results
        player_info = result['player']
        venue_info = result['venue']
        
        self.stdout.write(f"✅ PLAYER FOUND:")
        self.stdout.write(f"   • Name: {player_info['name']}")
        self.stdout.write(f"   • ID: {player_info['id']}")
        self.stdout.write(f"   • Team: {player_info['team']}")
        self.stdout.write(f"   • Position: {player_info['position']}")
        
        self.stdout.write(f"\n✅ VENUE FOUND:")
        self.stdout.write(f"   • Name: {venue_info['name']}")
        self.stdout.write(f"   • ID: {venue_info['id']}")
        self.stdout.write(f"   • City: {venue_info['city']}")
        
        self.stdout.write(f"\n📊 ANALYSIS RESULTS:")
        self.stdout.write(f"   • Seasons Analyzed: {result['seasons_analyzed']}")
        self.stdout.write(f"   • Games at {venue_name}: {result['games_at_venue']}")
        
        # Career stats
        career_stats = result.get('career_stats', {})
        if career_stats:
            self.stdout.write(f"\n🏏 CAREER HITTING STATISTICS:")
            self.stdout.write(f"   • Games: {career_stats.get('games', 'N/A')}")
            self.stdout.write(f"   • Batting Average: {career_stats.get('batting_average', 'N/A')}")
            self.stdout.write(f"   • Home Runs: {career_stats.get('home_runs', 'N/A')}")
            self.stdout.write(f"   • RBIs: {career_stats.get('rbis', 'N/A')}")
            self.stdout.write(f"   • OPS: {career_stats.get('ops', 'N/A')}")
        
        # Season stats
        season_stats = result.get('season_stats', {})
        for season_year, stats in season_stats.items():
            if stats:
                self.stdout.write(f"\n📈 {season_year} SEASON STATISTICS:")
                self.stdout.write(f"   • Games: {stats.get('games', 'N/A')}")
                self.stdout.write(f"   • Batting Average: {stats.get('batting_average', 'N/A')}")
                self.stdout.write(f"   • Home Runs: {stats.get('home_runs', 'N/A')}")
                self.stdout.write(f"   • RBIs: {stats.get('rbis', 'N/A')}")
                self.stdout.write(f"   • OPS: {stats.get('ops', 'N/A')}")
        
        # Sample games
        sample_games = result.get('sample_games', [])
        if sample_games:
            self.stdout.write(f"\n🎮 SAMPLE GAMES AT {venue_name}:")
            for i, game in enumerate(sample_games[:5], 1):
                self.stdout.write(f"   {i}. {game['date']}: {game['away_team']} @ {game['home_team']}")
        
        # Analysis summary
        summary = result.get('analysis_summary', {})
        if summary:
            self.stdout.write(f"\n📋 ANALYSIS SUMMARY:")
            self.stdout.write(f"   • Query: {summary.get('query', 'N/A')}")
            self.stdout.write(f"   • Data Sources: {', '.join(summary.get('data_sources', []))}")
            self.stdout.write(f"   • Games Found: {summary.get('games_found_at_venue', 'N/A')}")
            self.stdout.write(f"   • Has Career Data: {summary.get('has_career_data', 'N/A')}")

    def test_player_search(self, api, player_name):
        """Test enhanced player search capabilities"""
        self.stdout.write(f"\n🔍 TEST: Player Search for '{player_name}'")
        self.stdout.write("=" * 50)
        
        # Test player search
        search_result = api.search_players(player_name, active_only=False)
        
        query_results = search_result.get('search_player_all', {}).get('queryResults', {})
        total_size = query_results.get('totalSize', '0')
        
        self.stdout.write(f"✅ Search Results: {total_size} players found")
        
        if int(total_size) > 0:
            players = query_results.get('row', [])
            if not isinstance(players, list):
                players = [players]
            
            for i, player in enumerate(players[:5], 1):  # Show first 5 results
                self.stdout.write(f"   {i}. {player.get('name_display_first_last', 'Unknown')}")
                self.stdout.write(f"      Team: {player.get('team_full', 'N/A')}")
                self.stdout.write(f"      Position: {player.get('position', 'N/A')}")
                self.stdout.write(f"      ID: {player.get('player_id', 'N/A')}")
        
        # Test find specific player
        player = api.find_player_by_name(player_name, active_only=False)
        if player:
            self.stdout.write(f"\n✅ SPECIFIC PLAYER FOUND:")
            self.stdout.write(f"   • Name: {player.get('name_display_first_last', 'N/A')}")
            self.stdout.write(f"   • Team: {player.get('team_full', 'N/A')}")
            self.stdout.write(f"   • Position: {player.get('position', 'N/A')}")
            self.stdout.write(f"   • Bats/Throws: {player.get('bats', 'N/A')}/{player.get('throws', 'N/A')}")
        else:
            self.stdout.write(f"❌ Could not find specific player: {player_name}")
        
        # Test comprehensive profile
        profile = api.get_comprehensive_player_profile(player_name)
        if 'error' not in profile:
            self.stdout.write(f"\n📋 COMPREHENSIVE PROFILE:")
            basic_info = profile.get('basic_info', {})
            self.stdout.write(f"   • Name: {basic_info.get('name', 'N/A')}")
            self.stdout.write(f"   • Team: {basic_info.get('team', 'N/A')}")
            self.stdout.write(f"   • Position: {basic_info.get('position', 'N/A')}")
            
            career_stats = profile.get('career_stats', {})
            if career_stats:
                self.stdout.write(f"   • Career HR: {career_stats.get('home_runs', 'N/A')}")
                self.stdout.write(f"   • Career AVG: {career_stats.get('batting_average', 'N/A')}")

    def test_league_leaders(self, api, season):
        """Test league leaders functionality"""
        self.stdout.write(f"\n🏆 TEST: League Leaders for {season}")
        self.stdout.write("=" * 40)
        
        # Test comprehensive league leaders
        leaders_data = api.get_league_leaders_comprehensive(season, ['hr', 'rbi', 'avg'])
        
        if 'error' not in leaders_data:
            self.stdout.write(f"✅ League Leaders Data Retrieved for {season}")
            
            for category, data in leaders_data.get('categories', {}).items():
                if 'error' not in data:
                    stat_name = data.get('stat_name', category.upper())
                    leaders = data.get('leaders', [])
                    
                    self.stdout.write(f"\n🥇 {stat_name} LEADERS:")
                    for leader in leaders[:5]:  # Top 5
                        rank = leader.get('rank', 'N/A')
                        name = leader.get('name', 'Unknown')
                        value = leader.get('value', 'N/A')
                        self.stdout.write(f"   {rank}. {name}: {value}")
                else:
                    self.stdout.write(f"❌ Error getting {category} leaders: {data.get('error', 'Unknown')}")
        else:
            self.stdout.write(f"❌ Error getting league leaders: {leaders_data.get('error', 'Unknown')}")

    def summary_report(self):
        """Display implementation summary"""
        self.stdout.write(f"\n" + "=" * 70)
        self.stdout.write("🎯 ENHANCED MLB API - PHASE 1 IMPLEMENTATION SUMMARY")
        self.stdout.write("=" * 70)
        
        self.stdout.write("\n✅ IMPLEMENTED CAPABILITIES:")
        self.stdout.write("   • Player search by name (legacy API)")
        self.stdout.write("   • Comprehensive player profiles")
        self.stdout.write("   • Player venue performance analysis")
        self.stdout.write("   • Career and season statistics")
        self.stdout.write("   • League leaders and rankings")
        self.stdout.write("   • Modern + legacy API integration")
        
        self.stdout.write("\n🎪 USE CASES NOW SUPPORTED:")
        self.stdout.write("   • 'Aaron Judge hitting at Dodger Stadium'")
        self.stdout.write("   • 'Find player statistics by name'")
        self.stdout.write("   • 'Who leads the league in home runs?'")
        self.stdout.write("   • 'Get comprehensive player profile'")
        
        self.stdout.write("\n🚀 NEXT STEPS:")
        self.stdout.write("   • Integrate with database models")
        self.stdout.write("   • Add caching for performance")
        self.stdout.write("   • Implement natural language processing")
        self.stdout.write("   • Add advanced analytics endpoints")
        
        self.stdout.write("\n✅ STATUS: PHASE 1 COMPLETE - Ready for frontend LLM integration!")
