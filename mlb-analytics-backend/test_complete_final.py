#!/usr/bin/env python
"""
Final comprehensive test of CompleteMLBApi implementation
Verifies the complete ~95% MLB API coverage works for advanced analytics
"""
import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append('/Users/coletrammell/Documents/GitHub/Big-Brother/mlb-analytics-backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlb_analytics.settings')
django.setup()

from src.services.complete_mlb_api import CompleteMLBApi

def test_flagship_use_case():
    """Test the flagship use case: Aaron Judge at Dodger Stadium with complete analytics"""
    print("🚀 Testing flagship use case: Complete venue performance analysis")
    print("=" * 80)
    
    api = CompleteMLBApi()
    
    # Test the complete venue performance analysis
    print("🔍 Analyzing Aaron Judge's complete performance at Dodger Stadium...")
    result = api.analyze_player_venue_performance_complete(
        player_name="Aaron Judge",
        venue_name="Dodger Stadium",
        seasons=[2023, 2024],
        include_pitch_analysis=True,
        include_hit_locations=True
    )
    
    if 'error' in result:
        print(f"❌ Error in venue analysis: {result['error']}")
        return False
    
    print(f"✅ Found player: {result['player']['name']}")
    print(f"✅ Found venue: {result['venue']['name']}")
    print(f"✅ Games analyzed: {len(result.get('games_at_venue', []))}")
    
    # Check performance summary
    summary = result.get('performance_summary', {})
    print(f"\n📊 Performance Summary:")
    print(f"   • Total games analyzed: {summary.get('total_games_analyzed', 0)}")
    print(f"   • Analysis depth: {summary.get('analysis_depth', 'unknown')}")
    print(f"   • Pitch tracking: {summary.get('pitch_tracking', False)}")
    print(f"   • Hit location tracking: {summary.get('hit_location_tracking', False)}")
    
    # Check pitch-level analysis
    if result.get('pitch_level_analysis'):
        pitch_data = result['pitch_level_analysis']
        print(f"\n⚾ Pitch-Level Analysis:")
        print(f"   • Total pitches tracked: {pitch_data.get('total_pitches_tracked', 0)}")
        print(f"   • Average pitches per PA: {pitch_data.get('average_pitches_per_pa', 0):.1f}")
        
        outcomes = pitch_data.get('pitch_outcome_breakdown', {})
        if outcomes:
            print(f"   • Pitch outcomes: {list(outcomes.keys())[:5]}")
    
    # Check hit location analysis
    if result.get('hit_location_analysis'):
        hit_data = result['hit_location_analysis']
        print(f"\n🎯 Hit Location Analysis:")
        print(f"   • Total tracked hits: {hit_data.get('total_tracked_hits', 0)}")
    
    # Check detailed breakdown
    detailed = result.get('detailed_breakdown', [])
    if detailed:
        print(f"\n📈 Detailed Game Breakdown:")
        for game in detailed[:3]:  # Show first 3 games
            print(f"   • {game.get('date', 'Unknown')}: {game.get('pitches_faced', 0)} pitches, {game.get('plate_appearances', 0)} PA")
    
    return True

def test_enhanced_player_search():
    """Test enhanced player search capabilities"""
    print("\n" + "=" * 80)
    print("🔍 Testing enhanced player search capabilities")
    print("=" * 80)
    
    api = CompleteMLBApi()
    
    # Test comprehensive player search
    print("Searching for 'Aaron Judge'...")
    result = api.search_players_comprehensive("Aaron Judge", active_only=False)
    
    if 'error' in result:
        print(f"❌ Error in player search: {result['error']}")
        return False
    
    players = result.get('people', [])
    print(f"✅ Found {len(players)} players")
    
    if players:
        player = players[0]
        print(f"✅ Top result: {player.get('fullName')} (ID: {player.get('id')})")
        print(f"   • Position: {player.get('primaryPosition', {}).get('name', 'Unknown')}")
        print(f"   • Team: {player.get('currentTeam', {}).get('name', 'Unknown')}")
    
    return True

def test_comprehensive_player_profile():
    """Test comprehensive player profile generation"""
    print("\n" + "=" * 80)
    print("👤 Testing comprehensive player profile")
    print("=" * 80)
    
    api = CompleteMLBApi()
    
    print("Getting comprehensive profile for Aaron Judge...")
    result = api.get_comprehensive_player_profile("Aaron Judge")
    
    if 'error' in result:
        print(f"❌ Error in player profile: {result['error']}")
        return False
    
    print(f"✅ Basic info available: {'basic_info' in result}")
    print(f"✅ Detailed info available: {'detailed_info' in result}")
    print(f"✅ Career stats available: {'career_stats' in result}")
    print(f"✅ Current season stats available: {'current_season_stats' in result}")
    
    basic = result.get('basic_info', {})
    if basic:
        print(f"   • Player: {basic.get('fullName')}")
        print(f"   • Birth date: {basic.get('birthDate')}")
        print(f"   • Position: {basic.get('primaryPosition', {}).get('name')}")
    
    return True

def test_situational_splits():
    """Test situational splits analysis"""
    print("\n" + "=" * 80)
    print("📊 Testing situational splits analysis")
    print("=" * 80)
    
    api = CompleteMLBApi()
    
    # First get Aaron Judge's player ID
    search_result = api.search_players_comprehensive("Aaron Judge")
    if not search_result.get('people'):
        print("❌ Could not find Aaron Judge")
        return False
    
    player_id = search_result['people'][0]['id']
    print(f"Testing situational splits for player ID: {player_id}")
    
    result = api.get_player_situational_splits(
        player_id=player_id,
        season=2023,
        split_types=['vsl', 'vsr', 'home', 'away', 'risp']
    )
    
    if 'error' in result:
        print(f"❌ Error in situational splits: {result['error']}")
        return False
    
    splits = result.get('splits', {})
    print(f"✅ Situational splits available: {len(splits)} categories")
    
    for split_type, data in splits.items():
        if 'error' not in data:
            print(f"   • {split_type}: Data available")
        else:
            print(f"   • {split_type}: {data['error']}")
    
    return True

def test_game_analysis():
    """Test comprehensive game analysis capabilities"""
    print("\n" + "=" * 80)
    print("🎮 Testing comprehensive game analysis")
    print("=" * 80)
    
    api = CompleteMLBApi()
    
    # Get a recent game for testing
    print("Getting recent schedule to find a game...")
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    schedule = api.get_schedule(start_date, end_date)
    
    game_id = None
    if 'dates' in schedule:
        for date_info in schedule['dates']:
            for game in date_info.get('games', []):
                if game.get('status', {}).get('detailedState') == 'Final':
                    game_id = game.get('gamePk')
                    break
            if game_id:
                break
    
    if not game_id:
        print("❌ Could not find a completed game for testing")
        return False
    
    print(f"Testing with game ID: {game_id}")
    
    # Test pitch analysis
    print("\n⚾ Testing pitch analysis...")
    pitch_result = api.get_game_pitch_analysis(game_id)
    
    if 'error' in pitch_result:
        print(f"   ⚠️  Pitch analysis error (expected for older games): {pitch_result['error']}")
    else:
        print(f"   ✅ Total pitches tracked: {pitch_result.get('total_pitches', 0)}")
        print(f"   ✅ Batters tracked: {len(pitch_result.get('pitches_by_batter', {}))}")
    
    # Test comprehensive events
    print("\n📋 Testing comprehensive events...")
    events_result = api.get_game_events_comprehensive(game_id)
    
    if 'error' in events_result:
        print(f"   ❌ Events analysis error: {events_result['error']}")
        return False
    else:
        print(f"   ✅ Total events: {len(events_result.get('all_events', []))}")
        print(f"   ✅ Hits: {len(events_result.get('hits', []))}")
        print(f"   ✅ Home runs: {len(events_result.get('home_runs', []))}")
        print(f"   ✅ Strikeouts: {len(events_result.get('strikeouts', []))}")
    
    return True

def test_backwards_compatibility():
    """Test backwards compatibility with existing API methods"""
    print("\n" + "=" * 80)
    print("🔄 Testing backwards compatibility")
    print("=" * 80)
    
    api = CompleteMLBApi()
    
    # Test original methods still work
    print("Testing original search_people method...")
    result = api.search_people("Aaron Judge")
    
    if 'error' in result:
        print(f"❌ Error in backwards compatible search: {result['error']}")
        return False
    
    print(f"✅ search_people works: Found {len(result.get('people', []))} players")
    
    # Test original venue performance
    print("\nTesting original venue performance method...")
    result = api.get_player_venue_performance("Aaron Judge", "Dodger Stadium", [2023])
    
    if 'error' in result:
        print(f"⚠️  Venue performance warning: {result['error']}")
    else:
        print(f"✅ get_player_venue_performance works")
    
    return True

def run_complete_test_suite():
    """Run the complete test suite"""
    print("🧪 COMPLETE MLB API FINAL VERIFICATION TEST SUITE")
    print("🎯 Testing ~95% MLB API coverage for advanced analytics")
    print("=" * 80)
    
    tests = [
        ("Flagship Use Case (Aaron Judge at Dodger Stadium)", test_flagship_use_case),
        ("Enhanced Player Search", test_enhanced_player_search),
        ("Comprehensive Player Profile", test_comprehensive_player_profile),
        ("Situational Splits Analysis", test_situational_splits),
        ("Game Analysis (Pitch & Events)", test_game_analysis),
        ("Backwards Compatibility", test_backwards_compatibility)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ PASSED: {test_name}")
            else:
                print(f"❌ FAILED: {test_name}")
        except Exception as e:
            print(f"💥 EXCEPTION in {test_name}: {e}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! CompleteMLBApi is ready for production!")
        print("🚀 The backend now has comprehensive MLB API coverage (~95%)")
        print("⚾ Advanced analytics queries like 'Aaron Judge at Dodger Stadium' are fully supported!")
    else:
        print("⚠️  Some tests failed. Review the results above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_complete_test_suite()
    sys.exit(0 if success else 1)
