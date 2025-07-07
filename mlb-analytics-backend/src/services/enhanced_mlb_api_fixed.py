"""
Enhanced MLB API Service that provides comprehensive coverage of MLB data
Bridges both modern statsapi.mlb.com and legacy lookup-service-prod.mlb.com endpoints
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
import time
from .mlb_api import MLBApi, MLBApiError

logger = logging.getLogger(__name__)

class EnhancedMLBApi(MLBApi):
    """Extended MLB API service with comprehensive endpoint coverage"""
    
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
        
        cache_key = f"mlb_legacy_{endpoint}_{str(params)}"
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

    # ===== ENHANCED PLAYER ENDPOINTS =====
    
    def search_players(self, name_part: str, active_only: bool = True) -> Dict:
        """Search for players by name using comprehensive search"""
        params = {
            'sport_code': 'mlb',
            'name_part': f"{name_part}%25"  # Legacy API requires %25 for single terms
        }
        if active_only:
            params['active_sw'] = 'Y'
        else:
            params['active_sw'] = 'N'
            
        return self._make_legacy_request('search_player_all', params)
    
    def get_player_info_detailed(self, player_id: int) -> Dict:
        """Get comprehensive player information"""
        params = {
            'sport_code': 'mlb',
            'player_id': str(player_id)
        }
        return self._make_legacy_request('player_info', params)
    
    def get_player_team_history(self, player_id: int, season: Optional[int] = None) -> Dict:
        """Get all teams a player has played for"""
        params = {'player_id': str(player_id)}
        if season:
            params['season'] = str(season)
        return self._make_legacy_request('player_teams', params)
    
    def get_player_career_hitting(self, player_id: int, game_type: str = 'R') -> Dict:
        """Get player career hitting statistics"""
        params = {
            'league_list_id': 'mlb',
            'game_type': game_type,
            'player_id': str(player_id)
        }
        return self._make_legacy_request('sport_career_hitting', params)
    
    def get_player_career_pitching(self, player_id: int, game_type: str = 'R') -> Dict:
        """Get player career pitching statistics"""
        params = {
            'league_list_id': 'mlb',
            'game_type': game_type,
            'player_id': str(player_id)
        }
        return self._make_legacy_request('sport_career_pitching', params)
    
    def get_player_season_hitting(self, player_id: int, season: int, game_type: str = 'R') -> Dict:
        """Get player hitting stats for specific season"""
        params = {
            'league_list_id': 'mlb',
            'game_type': game_type,
            'season': str(season),
            'player_id': str(player_id)
        }
        return self._make_legacy_request('sport_hitting_tm', params)
    
    def get_player_season_pitching(self, player_id: int, season: int, game_type: str = 'R') -> Dict:
        """Get player pitching stats for specific season"""
        params = {
            'league_list_id': 'mlb',
            'game_type': game_type,
            'season': str(season),
            'player_id': str(player_id)
        }
        return self._make_legacy_request('sport_pitching_tm', params)
    
    def get_player_venue_performance(self, player_name: str, venue_name: str, seasons: Optional[List[int]] = None) -> Dict:
        """Get comprehensive player performance at specific venue"""
        try:
            # 1. Search for player
            search_result = self.search_players(player_name, active_only=False)
            if not search_result.get('search_player_all', {}).get('queryResults', {}).get('row'):
                return {'error': f"Player '{player_name}' not found"}
            
            # Handle single result vs multiple results
            player_data = search_result['search_player_all']['queryResults']['row']
            if isinstance(player_data, list):
                # Multiple players found, take first match
                player_data = player_data[0]
            
            player_id = player_data.get('player_id')
            if not player_id:
                return {'error': f"Could not find player ID for '{player_name}'"}
            
            # 2. Get all games at venue for seasons
            if not seasons:
                seasons = [self.get_current_season()]
            
            venue_games = []
            for season in seasons:
                try:
                    # Get all games for the season
                    start_date = f"{season}-03-01"
                    end_date = f"{season}-11-30"
                    schedule = self.get_schedule(start_date, end_date)
                    
                    # Filter games at the venue
                    if 'dates' in schedule:
                        for date_info in schedule['dates']:
                            for game in date_info.get('games', []):
                                venue_info = game.get('venue', {})
                                if venue_name.lower() in venue_info.get('name', '').lower():
                                    venue_games.append({
                                        'game_id': game.get('gamePk'),
                                        'date': game.get('gameDate'),
                                        'venue': venue_info.get('name'),
                                        'season': season
                                    })
                except Exception as e:
                    logger.warning(f"Error getting games for season {season}: {e}")
            
            # 3. Get player stats for those games
            performance_data = {
                'player': {
                    'name': player_data.get('name_display_first_last'),
                    'id': player_id,
                    'team': player_data.get('team_full', '')
                },
                'venue': venue_name,
                'seasons': seasons,
                'games_found': len(venue_games),
                'games': venue_games[:20],  # Limit to prevent huge responses
                'career_stats': {},
                'season_stats': {}
            }
            
            # 4. Get career stats
            try:
                career_hitting = self.get_player_career_hitting(int(player_id))
                if career_hitting.get('sport_career_hitting', {}).get('queryResults', {}).get('row'):
                    performance_data['career_stats']['hitting'] = career_hitting['sport_career_hitting']['queryResults']['row']
            except:
                pass
            
            # 5. Get season stats for each season
            for season in seasons:
                try:
                    season_hitting = self.get_player_season_hitting(int(player_id), season)
                    if season_hitting.get('sport_hitting_tm', {}).get('queryResults', {}).get('row'):
                        performance_data['season_stats'][str(season)] = season_hitting['sport_hitting_tm']['queryResults']['row']
                except:
                    pass
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error in get_player_venue_performance: {e}")
            return {'error': f"Failed to get player venue performance: {str(e)}"}
    
    def get_comprehensive_player_profile(self, player_name: str) -> Dict:
        """Get complete player profile with all available data"""
        try:
            # Search for player
            search_result = self.search_players(player_name, active_only=False)
            if not search_result.get('search_player_all', {}).get('queryResults', {}).get('row'):
                return {'error': f"Player '{player_name}' not found"}
            
            player_data = search_result['search_player_all']['queryResults']['row']
            if isinstance(player_data, list):
                player_data = player_data[0]
            
            player_id = int(player_data.get('player_id'))
            
            profile = {
                'basic_info': player_data,
                'detailed_info': {},
                'team_history': {},
                'career_stats': {},
                'current_season_stats': {}
            }
            
            # Get career stats
            try:
                career_hitting = self.get_player_career_hitting(player_id)
                if career_hitting.get('sport_career_hitting', {}).get('queryResults', {}).get('row'):
                    profile['career_stats']['hitting'] = career_hitting['sport_career_hitting']['queryResults']['row']
            except:
                pass
            
            # Get current season stats
            current_season = self.get_current_season()
            try:
                season_hitting = self.get_player_season_hitting(player_id, current_season)
                if season_hitting.get('sport_hitting_tm', {}).get('queryResults', {}).get('row'):
                    profile['current_season_stats']['hitting'] = season_hitting['sport_hitting_tm']['queryResults']['row']
            except:
                pass
            
            return profile
            
        except Exception as e:
            logger.error(f"Error in get_comprehensive_player_profile: {e}")
            return {'error': f"Failed to get comprehensive player profile: {str(e)}"}
    
    def get_hitting_leaders(self, stat: str, season: int, game_type: str = 'R', 
                           limit: int = 10, include_fields: Optional[List[str]] = None) -> Dict:
        """Get hitting statistical leaders"""
        params = {
            'sport_code': 'mlb',
            'results': str(limit),
            'game_type': game_type,
            'season': str(season),
            'sort_column': stat
        }
        if include_fields:
            params[f'leader_hitting_repeater.col_in'] = ','.join(include_fields)
        return self._make_legacy_request('leader_hitting_repeater', params)
    
    def get_pitching_leaders(self, stat: str, season: int, game_type: str = 'R', 
                            limit: int = 10, include_fields: Optional[List[str]] = None) -> Dict:
        """Get pitching statistical leaders"""
        params = {
            'sport_code': 'mlb',
            'results': str(limit),
            'game_type': game_type,
            'season': str(season),
            'sort_column': stat
        }
        if include_fields:
            params[f'leader_pitching_repeater.col_in'] = ','.join(include_fields)
        return self._make_legacy_request('leader_pitching_repeater', params)
    
    def get_transactions(self, start_date: str, end_date: str) -> Dict:
        """Get transactions over period (format: YYYYMMDD)"""
        params = {
            'sport_code': 'mlb',
            'start_date': start_date,
            'end_date': end_date
        }
        return self._make_legacy_request('transaction_all', params)
