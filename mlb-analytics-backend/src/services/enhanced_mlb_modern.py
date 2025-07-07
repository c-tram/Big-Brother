"""
Enhanced MLB API Service - Modern API Only
Simple enhancement of existing working MLB API service
"""
import logging
from typing import Dict, List, Optional
from .mlb_api import MLBApi

logger = logging.getLogger(__name__)

class EnhancedMLBApi(MLBApi):
    """Enhanced MLB API service using modern statsapi.mlb.com endpoints only"""
    
    def search_people(self, query: str, sport_id: int = 1, active_only: bool = True) -> Dict:
        """Search for people (players) by name"""
        params = {
            'names': query,
            'sportId': sport_id,
        }
        if active_only:
            params['active'] = 'true'
        
        return self._make_request('people/search', params)
    
    def get_person_details(self, person_id: int) -> Dict:
        """Get detailed person information"""
        params = {
            'hydrate': 'currentTeam,team,stats'
        }
        return self._make_request(f'people/{person_id}', params)
    
    def get_person_stats(self, person_id: int, stats: List[str], **kwargs) -> Dict:
        """Get person statistics"""
        params = {
            'stats': ','.join(stats),
            **kwargs
        }
        return self._make_request(f'people/{person_id}/stats', params)
    
    def get_league_leaders(self, leader_categories: List[str], season: int, limit: int = 10) -> Dict:
        """Get league leaders"""
        params = {
            'leaderCategories': ','.join(leader_categories),
            'season': season,
            'limit': limit
        }
        return self._make_request('stats/leaders', params)
    
    def find_player_by_name(self, player_name: str) -> Optional[Dict]:
        """Find a specific player by name and return their info"""
        try:
            search_result = self.search_people(player_name, active_only=False)
            if not search_result.get('people'):
                return None
            
            # Find best match
            for person in search_result['people']:
                if player_name.lower() in person.get('fullName', '').lower():
                    return person
            
            # Return first result if no exact match
            return search_result['people'][0]
            
        except Exception as e:
            logger.error(f"Error finding player {player_name}: {e}")
            return None
    
    def get_player_venue_performance(self, player_name: str, venue_name: str, seasons: Optional[List[int]] = None) -> Dict:
        """
        Analyze player performance at a specific venue
        This is our enhanced capability for queries like 'Aaron Judge at Dodger Stadium'
        """
        try:
            if not seasons:
                seasons = [self.get_current_season()]
            
            # Step 1: Find the player
            player = self.find_player_by_name(player_name)
            if not player:
                return {'error': f"Player '{player_name}' not found"}
            
            # Step 2: Find the venue
            venues = self.get_venues()
            venue = None
            for v in venues.get('venues', []):
                if venue_name.lower() in v.get('name', '').lower():
                    venue = v
                    break
            
            if not venue:
                return {'error': f"Venue '{venue_name}' not found"}
            
            # Step 3: Get player career stats
            player_id = player['id']
            career_stats = self.get_person_stats(player_id, ['career'])
            
            # Step 4: Get season stats for each requested season
            season_stats = {}
            for season in seasons:
                try:
                    stats = self.get_person_stats(player_id, ['season'], season=season)
                    if stats.get('stats'):
                        season_stats[str(season)] = stats['stats']
                except Exception as e:
                    logger.warning(f"Could not get {season} stats for {player_name}: {e}")
            
            # Step 5: Get games at the venue (for context)
            venue_games = []
            for season in seasons:
                try:
                    start_date = f"{season}-03-01"
                    end_date = f"{season}-11-30"
                    
                    # Get all games for the season, then filter by venue
                    schedule = self.get_schedule(start_date, end_date)
                    
                    if 'dates' in schedule:
                        for date_info in schedule['dates']:
                            for game in date_info.get('games', []):
                                # Check if game is at the target venue
                                game_venue = game.get('venue', {})
                                if game_venue.get('id') == venue['id']:
                                    venue_games.append({
                                        'game_id': game.get('gamePk'),
                                        'date': game.get('gameDate'),
                                        'home_team': game.get('teams', {}).get('home', {}).get('team', {}).get('name'),
                                        'away_team': game.get('teams', {}).get('away', {}).get('team', {}).get('name'),
                                        'season': season,
                                        'venue_confirmed': game_venue.get('name')
                                    })
                except Exception as e:
                    logger.warning(f"Could not get venue games for {season}: {e}")
            
            # Compile results
            result = {
                'player': {
                    'id': player_id,
                    'name': player.get('fullName'),
                    'position': player.get('primaryPosition', {}).get('name'),
                    'current_team': player.get('currentTeam', {}).get('name')
                },
                'venue': {
                    'id': venue['id'],
                    'name': venue.get('name'),
                    'city': venue.get('location', {}).get('city'),
                    'state': venue.get('location', {}).get('stateAbbrev')
                },
                'analysis': {
                    'seasons_analyzed': seasons,
                    'total_venue_games': len(venue_games),
                    'sample_games': venue_games[:5]  # Show first 5 games
                },
                'career_stats': career_stats.get('stats', []),
                'season_stats': season_stats,
                'methodology': 'Modern MLB API analysis using statsapi.mlb.com endpoints'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in venue performance analysis: {e}")
            return {'error': f"Analysis failed: {str(e)}"}
    
    def get_comprehensive_player_profile(self, player_name: str) -> Dict:
        """Get complete player profile"""
        try:
            # Find player
            player = self.find_player_by_name(player_name)
            if not player:
                return {'error': f"Player '{player_name}' not found"}
            
            player_id = player['id']
            
            # Get detailed info
            detailed_info = self.get_person_details(player_id)
            
            # Get career stats
            career_stats = self.get_person_stats(player_id, ['career'])
            
            # Get current season stats
            current_season = self.get_current_season()
            season_stats = self.get_person_stats(player_id, ['season'], season=current_season)
            
            return {
                'basic_info': player,
                'detailed_info': detailed_info.get('people', [{}])[0] if detailed_info.get('people') else {},
                'career_stats': career_stats.get('stats', []),
                'current_season_stats': season_stats.get('stats', []),
                'api_coverage': 'Enhanced modern MLB API'
            }
            
        except Exception as e:
            logger.error(f"Error getting player profile: {e}")
            return {'error': f"Profile retrieval failed: {str(e)}"}
