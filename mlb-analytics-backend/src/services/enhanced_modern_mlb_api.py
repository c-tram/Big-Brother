"""
Enhanced MLB API Service using ONLY the modern statsapi.mlb.com endpoints
Maximizes coverage without legacy API dependencies
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

class EnhancedModernMLBApi(MLBApi):
    """Enhanced MLB API service using only modern statsapi.mlb.com endpoints"""
    
    def __init__(self):
        super().__init__()
        # Extended hydration parameters for comprehensive data
        self.COMPREHENSIVE_HYDRATE = [
            'person', 'team', 'venue', 'game', 'linescore', 'boxscore',
            'stats', 'probablePitcher', 'decisions', 'plays', 'highlights',
            'weather', 'officials', 'seriesStatus', 'broadcasts'
        ]
    
    def search_people(self, query: str, sport_id: int = 1, active_only: bool = True) -> Dict:
        """Search for people (players, coaches, etc.) by name using modern API"""
        params = {
            'names': query,
            'sportId': sport_id,
        }
        if active_only:
            params['active'] = 'true'
        
        return self._make_request('people/search', params)
    
    def get_person_details(self, person_id: int, hydrate: Optional[List[str]] = None) -> Dict:
        """Get comprehensive person details"""
        if hydrate is None:
            hydrate = ['currentTeam', 'team', 'stats', 'awards', 'education', 'transactions']
        
        params = {'hydrate': ','.join(hydrate)}
        return self._make_request(f'people/{person_id}', params)
    
    def get_person_stats(self, person_id: int, stats: List[str], **kwargs) -> Dict:
        """Get detailed person statistics with flexible parameters"""
        params = {
            'stats': ','.join(stats),
            **kwargs
        }
        return self._make_request(f'people/{person_id}/stats', params)
    
    def get_player_game_logs(self, person_id: int, season: int, game_type: str = 'R') -> Dict:
        """Get player's game-by-game performance for a season"""
        params = {
            'season': season,
            'gameType': game_type,
            'hydrate': 'team,opponent,venue'
        }
        return self._make_request(f'people/{person_id}/stats/game/{season}', params)
    
    def get_venue_details(self, venue_id: int, hydrate: Optional[List[str]] = None) -> Dict:
        """Get comprehensive venue information"""
        if hydrate is None:
            hydrate = ['location', 'fieldInfo', 'timezone']
        
        params = {'hydrate': ','.join(hydrate)}
        return self._make_request(f'venues/{venue_id}', params)
    
    def get_games_by_venue(self, venue_id: int, start_date: str, end_date: str, 
                          season: Optional[int] = None) -> Dict:
        """Get all games at a specific venue within date range"""
        params = {
            'venueIds': venue_id,
            'startDate': start_date,
            'endDate': end_date,
            'hydrate': ','.join(['team', 'venue', 'linescore', 'boxscore'])
        }
        if season:
            params['season'] = season
        
        return self._make_request('schedule', params)
    
    def get_comprehensive_game_data(self, game_id: int) -> Dict:
        """Get all available data for a specific game"""
        hydrate_params = [
            'venue', 'team', 'linescore', 'boxscore', 'plays', 'playByPlay',
            'probablePitcher', 'weather', 'officials', 'broadcasts', 'decisions'
        ]
        
        params = {'hydrate': ','.join(hydrate_params)}
        return self._make_request(f'game/{game_id}', params)
    
    def get_league_leaders(self, leader_categories: List[str], season: int, 
                          league_id: Optional[int] = None, limit: int = 10) -> Dict:
        """Get league leaders for specified categories"""
        params = {
            'leaderCategories': ','.join(leader_categories),
            'season': season,
            'limit': limit
        }
        if league_id:
            params['leagueId'] = league_id
        
        return self._make_request('stats/leaders', params)
    
    def get_team_stats(self, team_ids: List[int], stats: List[str], season: int, **kwargs) -> Dict:
        """Get team statistics"""
        params = {
            'teamIds': ','.join(map(str, team_ids)),
            'stats': ','.join(stats),
            'season': season,
            **kwargs
        }
        return self._make_request('teams/stats', params)
    
    def get_player_venue_performance(self, player_name: str, venue_name: str, 
                                   seasons: Optional[List[int]] = None) -> Dict:
        """
        Get comprehensive player performance at specific venue using modern API
        This is our flagship enhanced capability
        """
        try:
            if not seasons:
                seasons = [self.get_current_season()]
            
            # Step 1: Search for player
            search_result = self.search_people(player_name, active_only=False)
            if not search_result.get('people'):
                return {'error': f"Player '{player_name}' not found"}
            
            # Find best match
            player = None
            for person in search_result['people']:
                if player_name.lower() in person.get('fullName', '').lower():
                    player = person
                    break
            
            if not player:
                player = search_result['people'][0]  # Take first result
            
            player_id = player['id']
            
            # Step 2: Find venue
            venues = self.get_venues()
            venue = None
            venue_id = None
            
            for v in venues.get('venues', []):
                if venue_name.lower() in v.get('name', '').lower():
                    venue = v
                    venue_id = v['id']
                    break
            
            if not venue_id:
                return {'error': f"Venue '{venue_name}' not found"}
            
            # Step 3: Get games at venue for each season
            all_games = []
            player_games = []
            
            for season in seasons:
                try:
                    # Get all games at venue for season
                    start_date = f"{season}-03-01"
                    end_date = f"{season}-11-30"
                    
                    games_at_venue = self.get_games_by_venue(venue_id, start_date, end_date, season)
                    
                    if 'dates' in games_at_venue:
                        for date_info in games_at_venue['dates']:
                            for game in date_info.get('games', []):
                                all_games.append(game)
                                
                                # Check if player's team was involved
                                home_team = game.get('teams', {}).get('home', {}).get('team', {})
                                away_team = game.get('teams', {}).get('away', {}).get('team', {})
                                
                                # Get player's team info
                                player_details = self.get_person_details(player_id)
                                if 'people' in player_details and player_details['people']:
                                    current_team = player_details['people'][0].get('currentTeam', {})
                                    player_team_id = current_team.get('id')
                                    
                                    if (player_team_id == home_team.get('id') or 
                                        player_team_id == away_team.get('id')):
                                        player_games.append({
                                            'game': game,
                                            'season': season,
                                            'date': game.get('gameDate'),
                                            'game_id': game.get('gamePk')
                                        })
                except Exception as e:
                    logger.warning(f"Error getting games for season {season}: {e}")
            
            # Step 4: Get player statistics and game logs
            player_stats = {}
            game_logs = {}
            
            for season in seasons:
                try:
                    # Get season stats
                    season_stats = self.get_person_stats(
                        player_id, 
                        ['season'], 
                        season=season
                    )
                    if season_stats.get('stats'):
                        player_stats[str(season)] = season_stats['stats']
                    
                    # Get game logs
                    logs = self.get_player_game_logs(player_id, season)
                    if logs.get('stats'):
                        game_logs[str(season)] = logs['stats']
                        
                except Exception as e:
                    logger.warning(f"Error getting player stats for season {season}: {e}")
            
            # Step 5: Get career stats
            career_stats = {}
            try:
                career_data = self.get_person_stats(player_id, ['career'])
                if career_data.get('stats'):
                    career_stats = career_data['stats']
            except Exception as e:
                logger.warning(f"Error getting career stats: {e}")
            
            # Compile comprehensive result
            result = {
                'player': {
                    'id': player_id,
                    'name': player.get('fullName'),
                    'first_name': player.get('firstName'),
                    'last_name': player.get('lastName'),
                    'primary_position': player.get('primaryPosition', {}).get('name'),
                    'current_team': player.get('currentTeam', {}).get('name')
                },
                'venue': {
                    'id': venue_id,
                    'name': venue.get('name'),
                    'city': venue.get('location', {}).get('city'),
                    'state': venue.get('location', {}).get('stateAbbrev')
                },
                'analysis_period': {
                    'seasons': seasons,
                    'total_games_at_venue': len(all_games),
                    'player_games_at_venue': len(player_games)
                },
                'games': player_games[:10],  # Sample of games
                'season_stats': player_stats,
                'game_logs': game_logs,
                'career_stats': career_stats,
                'venue_performance_summary': {
                    'games_played': len(player_games),
                    'seasons_analyzed': len(seasons),
                    'venue_games_available': len(all_games)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in get_player_venue_performance: {e}")
            return {'error': f"Failed to analyze player venue performance: {str(e)}"}
    
    def get_comprehensive_player_profile(self, player_name: str) -> Dict:
        """Get complete player profile using modern API"""
        try:
            # Search for player
            search_result = self.search_people(player_name, active_only=False)
            if not search_result.get('people'):
                return {'error': f"Player '{player_name}' not found"}
            
            # Find best match
            player = None
            for person in search_result['people']:
                if player_name.lower() in person.get('fullName', '').lower():
                    player = person
                    break
            
            if not player:
                player = search_result['people'][0]
            
            player_id = player['id']
            
            # Get detailed player information
            detailed_info = self.get_person_details(player_id)
            
            # Get career stats
            career_stats = self.get_person_stats(player_id, ['career'])
            
            # Get current season stats
            current_season = self.get_current_season()
            season_stats = self.get_person_stats(player_id, ['season'], season=current_season)
            
            # Compile profile
            profile = {
                'basic_info': player,
                'detailed_info': detailed_info.get('people', [{}])[0] if detailed_info.get('people') else {},
                'career_stats': career_stats.get('stats', []),
                'current_season_stats': season_stats.get('stats', []),
                'search_metadata': {
                    'search_term': player_name,
                    'total_matches': len(search_result.get('people', [])),
                    'selected_match': player.get('fullName')
                }
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error in get_comprehensive_player_profile: {e}")
            return {'error': f"Failed to get comprehensive player profile: {str(e)}"}
    
    def get_advanced_team_analysis(self, team_id: int, season: int) -> Dict:
        """Get comprehensive team analysis"""
        try:
            # Get team details
            team_details = self.get_team(team_id)
            
            # Get team stats
            team_stats = self.get_team_stats([team_id], ['season'], season)
            
            # Get team roster
            roster = self.get_team_roster(team_id, season=season)
            
            # Get team schedule
            schedule = self.get_team_schedule(team_id, season=season)
            
            return {
                'team_details': team_details,
                'season_stats': team_stats,
                'roster': roster,
                'schedule_summary': {
                    'total_games': len(schedule.get('dates', [])),
                    'recent_games': schedule.get('dates', [])[-5:] if schedule.get('dates') else []
                }
            }
            
        except Exception as e:
            logger.error(f"Error in get_advanced_team_analysis: {e}")
            return {'error': f"Failed to get team analysis: {str(e)}"}
