import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
import time

logger = logging.getLogger(__name__)

class MLBApiError(Exception):
    """Custom exception for MLB API errors"""
    pass

class MLBApi:
    BASE_URL = getattr(settings, 'MLB_API_BASE_URL', 'https://statsapi.mlb.com/api/v1')
    TIMEOUT = getattr(settings, 'MLB_API_TIMEOUT', 30)
    RATE_LIMIT = getattr(settings, 'MLB_API_RATE_LIMIT', 60)
    
    def __init__(self):
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window = 60  # seconds
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a rate-limited request to the MLB API"""
        current_time = time.time()
        
        # Simple rate limiting
        if current_time - self.last_request_time < (60 / self.RATE_LIMIT):
            time.sleep((60 / self.RATE_LIMIT) - (current_time - self.last_request_time))
        
        cache_key = f"mlb_api_{endpoint}_{str(params)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            # Cache for 5 minutes
            cache.set(cache_key, data, 300)
            
            self.last_request_time = time.time()
            logger.info(f"MLB API request successful: {url}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MLB API request failed: {url}, Error: {str(e)}")
            raise MLBApiError(f"API request failed: {str(e)}")
    
    # Team endpoints
    def get_teams(self, sport_id: int = 1) -> Dict:
        """Get all MLB teams"""
        return self._make_request('teams', {'sportId': sport_id})
    
    def get_team(self, team_id: int) -> Dict:
        """Get specific team details"""
        return self._make_request(f'teams/{team_id}')
    
    def get_team_roster(self, team_id: int, season: Optional[int] = None) -> Dict:
        """Get team roster"""
        params = {}
        if season:
            params['season'] = season
        return self._make_request(f'teams/{team_id}/roster', params)
    
    def get_team_stats(self, team_id: int, season: Optional[int] = None) -> Dict:
        """Get team stats"""
        params = {}
        if season:
            params['season'] = season
        return self._make_request(f'teams/{team_id}/stats', params)
    
    # Player endpoints
    def get_player(self, player_id: int) -> Dict:
        """Get specific player details"""
        return self._make_request(f'people/{player_id}')
    
    def get_player_stats(self, player_id: int, season: Optional[int] = None, 
                        stat_type: str = 'season') -> Dict:
        """Get player stats"""
        params = {'stats': stat_type}
        if season:
            params['season'] = season
        return self._make_request(f'people/{player_id}/stats', params)
    
    # Game endpoints
    def get_schedule(self, start_date: str, end_date: str, team_id: Optional[int] = None) -> Dict:
        """Get game schedule"""
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'sportId': 1
        }
        if team_id:
            params['teamId'] = team_id
        return self._make_request('schedule', params)
    
    def get_game(self, game_id: int) -> Dict:
        """Get specific game details"""
        return self._make_request(f'game/{game_id}/feed/live')
    
    def get_game_boxscore(self, game_id: int) -> Dict:
        """Get game boxscore"""
        return self._make_request(f'game/{game_id}/boxscore')
    
    def get_game_linescore(self, game_id: int) -> Dict:
        """Get game linescore"""
        return self._make_request(f'game/{game_id}/linescore')
    
    def get_games_by_date(self, date: str) -> Dict:
        """Get all games for a specific date"""
        return self._make_request('schedule', {
            'date': date,
            'sportId': 1
        })
    
    # Season and standings endpoints
    def get_standings(self, league_id: Optional[int] = None, season: Optional[int] = None) -> Dict:
        """Get league standings"""
        params = {}
        if league_id:
            params['leagueId'] = league_id
        if season:
            params['season'] = season
        return self._make_request('standings', params)
    
    def get_seasons(self, sport_id: int = 1) -> Dict:
        """Get available seasons"""
        return self._make_request('seasons', {'sportId': sport_id})
    
    # Statistics endpoints
    def get_league_leaders(self, stat_type: str, season: Optional[int] = None, 
                          league_id: Optional[int] = None) -> Dict:
        """Get league leaders for specific stat"""
        params = {'leaderCategories': stat_type}
        if season:
            params['season'] = season
        if league_id:
            params['leagueId'] = league_id
        return self._make_request('stats/leaders', params)
    
    def get_team_stats_leaders(self, team_id: int, stat_type: str, 
                              season: Optional[int] = None) -> Dict:
        """Get team statistical leaders"""
        params = {
            'stats': stat_type,
            'group': 'hitting,pitching,fielding'
        }
        if season:
            params['season'] = season
        return self._make_request(f'teams/{team_id}/stats/leaders', params)
    
    # Venues and divisions
    def get_venues(self) -> Dict:
        """Get all MLB venues"""
        return self._make_request('venues')
    
    def get_venue(self, venue_id: int) -> Dict:
        """Get specific venue details"""
        return self._make_request(f'venues/{venue_id}')
    
    def get_divisions(self) -> Dict:
        """Get all MLB divisions"""
        return self._make_request('divisions')
    
    def get_leagues(self) -> Dict:
        """Get all MLB leagues"""
        return self._make_request('leagues')
    
    # Utility methods
    def get_current_season(self) -> int:
        """Get current MLB season year"""
        current_year = datetime.now().year
        # MLB season typically runs from March to October
        if datetime.now().month >= 3:
            return current_year
        else:
            return current_year - 1
    
    def get_date_range_games(self, days_back: int = 7) -> Dict:
        """Get games for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        return self.get_schedule(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )