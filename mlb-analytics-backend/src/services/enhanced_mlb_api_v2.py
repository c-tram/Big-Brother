"""
Enhanced MLB API Service - Phase 1 Implementation
Provides comprehensive MLB data coverage by bridging modern + legacy APIs
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from django.conf import settings
from django.core.cache import cache
import time
from .mlb_api import MLBApi, MLBApiError

logger = logging.getLogger(__name__)

class EnhancedMLBApiV2(MLBApi):
    """
    Enhanced MLB API service with comprehensive endpoint coverage
    Bridges statsapi.mlb.com (modern) + lookup-service-prod.mlb.com (legacy)
    """
    
    LEGACY_BASE_URL = 'http://lookup-service-prod.mlb.com'
    
    def __init__(self):
        super().__init__()
        self.legacy_cache_timeout = 600  # 10 minutes for legacy API calls
    
    def _make_legacy_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the legacy MLB lookup service"""
        current_time = time.time()
        
        # Rate limiting
        if current_time - self.last_request_time < (60 / self.RATE_LIMIT):
            time.sleep((60 / self.RATE_LIMIT) - (current_time - self.last_request_time))
        
        # Create clean cache key
        cache_key = f"mlb_legacy_{endpoint}_{hash(str(params))}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        url = f"{self.LEGACY_BASE_URL}/json/named.{endpoint}.bam"
        
        try:
            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            cache.set(cache_key, data, self.legacy_cache_timeout)
            
            self.last_request_time = time.time()
            logger.info(f"MLB Legacy API request successful: {url}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MLB Legacy API request failed: {url}, Error: {str(e)}")
            raise MLBApiError(f"Legacy API request failed: {str(e)}")

    def search_players(self, name_part: str, active_only: bool = True) -> Dict:
        """Search for players by name using comprehensive search"""
        # Handle single word searches that need %25 suffix
        search_term = name_part
        if ' ' not in name_part:
            search_term = f"{name_part}%25"
        
        params = {
            'sport_code': 'mlb',
            'name_part': search_term
        }
        if active_only:
            params['active_sw'] = 'Y'
        else:
            params['active_sw'] = 'N'
            
        return self._make_legacy_request('search_player_all', params)
    
    def find_player_by_name(self, name: str, active_only: bool = True) -> Optional[Dict]:
        """Find a specific player by full or partial name"""
        try:
            result = self.search_players(name, active_only)
            
            query_results = result.get('search_player_all', {}).get('queryResults', {})
            if not query_results or query_results.get('totalSize') == '0':
                return None
            
            players = query_results.get('row', [])
            if not players:
                return None
            
            # If single result, return it
            if not isinstance(players, list):
                return players
            
            # If multiple results, find best match
            name_lower = name.lower()
            for player in players:
                full_name = player.get('name_display_first_last', '').lower()
                if name_lower in full_name or full_name in name_lower:
                    return player
            
            # Return first result if no exact match
            return players[0]
            
        except Exception as e:
            logger.error(f"Error finding player {name}: {e}")
            return None

    def get_player_venue_performance(self, player_name: str, venue_name: str, 
                                   seasons: Optional[List[int]] = None) -> Dict:
        """
        Get comprehensive player performance at specific venue
        This is the key method for 'Aaron Judge at Dodger Stadium' queries
        """
        try:
            # 1. Find the player
            player = self.find_player_by_name(player_name, active_only=False)
            if not player:
                return {'error': f"Player '{player_name}' not found"}
            
            player_id = player.get('player_id')
            if not player_id:
                return {'error': f"Could not find player ID for '{player_name}'"}
            
            # 2. Find the venue
            venues = self.get_venues()
            target_venue = None
            for venue in venues.get('venues', []):
                if venue_name.lower() in venue.get('name', '').lower():
                    target_venue = venue
                    break
            
            if not target_venue:
                return {'error': f"Venue '{venue_name}' not found"}
            
            # 3. Get seasons to analyze
            if not seasons:
                seasons = [self.get_current_season()]
            
            # 4. Build comprehensive response
            performance_data = {
                'player': {
                    'name': player.get('name_display_first_last'),
                    'id': player_id,
                    'team': player.get('team_full', ''),
                    'position': player.get('position', 'N/A')
                },
                'venue': {
                    'name': target_venue.get('name'),
                    'id': target_venue.get('id'),
                    'city': target_venue.get('location', {}).get('city', 'N/A')
                },
                'seasons_analyzed': seasons,
                'career_stats': {},
                'analysis_summary': {
                    'query': f"{player_name} performance at {venue_name}",
                    'data_sources': ['MLB Stats API', 'MLB Legacy API'],
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # 5. Get career hitting stats using legacy API
            try:
                career_data = self._make_legacy_request('sport_career_hitting', {
                    'league_list_id': 'mlb',
                    'game_type': 'R',
                    'player_id': str(player_id)
                })
                
                career_row = career_data.get('sport_career_hitting', {}).get('queryResults', {}).get('row')
                if career_row:
                    performance_data['career_stats'] = {
                        'games': career_row.get('g', 'N/A'),
                        'at_bats': career_row.get('ab', 'N/A'),
                        'hits': career_row.get('h', 'N/A'),
                        'batting_average': career_row.get('avg', 'N/A'),
                        'home_runs': career_row.get('hr', 'N/A'),
                        'rbis': career_row.get('rbi', 'N/A'),
                        'ops': career_row.get('ops', 'N/A'),
                        'slugging': career_row.get('slg', 'N/A'),
                        'obp': career_row.get('obp', 'N/A')
                    }
                    performance_data['analysis_summary']['has_career_data'] = True
            except Exception as e:
                logger.warning(f"Could not get career stats: {e}")
                performance_data['analysis_summary']['has_career_data'] = False
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error in get_player_venue_performance: {e}")
            return {'error': f"Failed to analyze player venue performance: {str(e)}"}
    
    def get_comprehensive_player_profile(self, player_name: str) -> Dict:
        """Get complete player profile with all available data"""
        try:
            # Find the player
            player = self.find_player_by_name(player_name, active_only=False)
            if not player:
                return {'error': f"Player '{player_name}' not found"}
            
            return {
                'basic_info': {
                    'name': player.get('name_display_first_last'),
                    'id': player.get('player_id'),
                    'team': player.get('team_full', 'N/A'),
                    'position': player.get('position', 'N/A'),
                    'bats': player.get('bats', 'N/A'),
                    'throws': player.get('throws', 'N/A')
                },
                'data_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in get_comprehensive_player_profile: {e}")
            return {'error': f"Failed to get comprehensive player profile: {str(e)}"}
