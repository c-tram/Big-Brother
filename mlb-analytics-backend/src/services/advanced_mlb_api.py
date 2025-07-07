"""
Advanced MLB API Service - Complete Baseball Analytics
Extends the working enhanced API with comprehensive play-by-play analysis
"""
import logging
from typing import Dict, List, Optional
from .enhanced_mlb_modern import EnhancedMLBApi

logger = logging.getLogger(__name__)

class AdvancedMLBApi(EnhancedMLBApi):
    """
    Advanced MLB API service with complete baseball analytics capabilities
    Focuses on play-by-play analysis and comprehensive performance metrics
    """
    
    def get_game_play_by_play(self, game_id: int) -> Dict:
        """
        Get detailed play-by-play data for comprehensive game analysis
        CRITICAL for understanding what happened in each at-bat
        """
        params = {'hydrate': 'plays,playByPlay,decisions,person'}
        return self._make_request(f'game/{game_id}', params)
    
    def get_game_pitch_data(self, game_id: int) -> Dict:
        """
        Get pitch-by-pitch data including location, velocity, type
        Essential for understanding HOW players performed in specific situations
        """
        try:
            # Get the game data with plays
            game_data = self.get_game_play_by_play(game_id)
            
            if 'liveData' not in game_data:
                return {'error': 'No live data available for this game'}
            
            plays = game_data.get('liveData', {}).get('plays', {}).get('allPlays', [])
            
            pitch_data = {
                'game_id': game_id,
                'total_pitches': 0,
                'pitches_by_inning': {},
                'pitches_by_batter': {},
                'pitches_by_pitcher': {},
                'all_pitches': []
            }
            
            for play in plays:
                if 'playEvents' in play:
                    for event in play['playEvents']:
                        if event.get('isPitch', False):
                            pitch_info = {
                                'inning': play.get('about', {}).get('inning'),
                                'half_inning': play.get('about', {}).get('halfInning'),
                                'batter_id': play.get('matchup', {}).get('batter', {}).get('id'),
                                'pitcher_id': play.get('matchup', {}).get('pitcher', {}).get('id'),
                                'pitch_data': event.get('pitchData', {}),
                                'hit_data': event.get('hitData', {}),
                                'details': event.get('details', {}),
                                'count': event.get('count', {}),
                                'pitch_number': event.get('pitchNumber'),
                                'type': event.get('type'),
                                'description': event.get('details', {}).get('description')
                            }
                            
                            pitch_data['all_pitches'].append(pitch_info)
                            pitch_data['total_pitches'] += 1
                            
                            # Group by batter
                            batter_id = pitch_info['batter_id']
                            if batter_id not in pitch_data['pitches_by_batter']:
                                pitch_data['pitches_by_batter'][batter_id] = []
                            pitch_data['pitches_by_batter'][batter_id].append(pitch_info)
                            
                            # Group by pitcher
                            pitcher_id = pitch_info['pitcher_id']
                            if pitcher_id not in pitch_data['pitches_by_pitcher']:
                                pitch_data['pitches_by_pitcher'][pitcher_id] = []
                            pitch_data['pitches_by_pitcher'][pitcher_id].append(pitch_info)
            
            return pitch_data
            
        except Exception as e:
            logger.error(f"Error getting pitch data for game {game_id}: {e}")
            return {'error': f"Failed to get pitch data: {str(e)}"}
    
    def get_game_events(self, game_id: int) -> Dict:
        """Get all significant game events (hits, runs, errors, etc.)"""
        try:
            game_data = self.get_comprehensive_game_data(game_id)
            
            if 'liveData' not in game_data:
                return {'error': 'No live data available'}
            
            plays = game_data.get('liveData', {}).get('plays', {}).get('allPlays', [])
            
            events = {
                'game_id': game_id,
                'scoring_plays': [],
                'hits': [],
                'errors': [],
                'strikeouts': [],
                'home_runs': [],
                'stolen_bases': [],
                'all_events': []
            }
            
            for play in plays:
                result = play.get('result', {})
                event_type = result.get('event')
                
                event_info = {
                    'inning': play.get('about', {}).get('inning'),
                    'half_inning': play.get('about', {}).get('halfInning'),
                    'batter': play.get('matchup', {}).get('batter'),
                    'pitcher': play.get('matchup', {}).get('pitcher'),
                    'event_type': event_type,
                    'description': result.get('description'),
                    'rbi': result.get('rbi', 0),
                    'runs_scored': len(play.get('runners', [])) if 'runners' in play else 0
                }
                
                events['all_events'].append(event_info)
                
                # Categorize events
                if result.get('rbi', 0) > 0 or event_info['runs_scored'] > 0:
                    events['scoring_plays'].append(event_info)
                
                if event_type in ['Single', 'Double', 'Triple', 'Home Run']:
                    events['hits'].append(event_info)
                    
                if event_type == 'Home Run':
                    events['home_runs'].append(event_info)
                    
                if event_type == 'Strikeout':
                    events['strikeouts'].append(event_info)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting game events for game {game_id}: {e}")
            return {'error': f"Failed to get game events: {str(e)}"}
    
    def get_player_situational_stats(self, player_id: int, season: int, 
                                   situations: Optional[List[str]] = None) -> Dict:
        """
        Get detailed situational statistics (vs LHP/RHP, home/away, RISP, etc.)
        Addresses the critical gap in situational analysis
        """
        try:
            if not situations:
                situations = ['vsl', 'vsr', 'home', 'away', 'risp', 'bases_empty']
            
            situational_data = {
                'player_id': player_id,
                'season': season,
                'situations': {}
            }
            
            for situation in situations:
                try:
                    # Get stats for this situation
                    params = {
                        'stats': 'season',
                        'season': season,
                        'group': 'hitting',
                        'sitCodes': situation
                    }
                    
                    stats = self._make_request(f'people/{player_id}/stats', params)
                    situational_data['situations'][situation] = stats
                    
                except Exception as e:
                    logger.warning(f"Could not get {situation} stats: {e}")
                    situational_data['situations'][situation] = {'error': str(e)}
            
            return situational_data
            
        except Exception as e:
            logger.error(f"Error getting situational stats: {e}")
            return {'error': f"Failed to get situational stats: {str(e)}"}
    
    def analyze_player_at_venue_advanced(self, player_name: str, venue_name: str, 
                                       seasons: Optional[List[int]] = None,
                                       include_pitch_analysis: bool = True) -> Dict:
        """
        ADVANCED venue performance analysis with pitch-level data
        This is the flagship method for comprehensive baseball analytics
        """
        try:
            if not seasons:
                seasons = [self.get_current_season()]
            
            # Start with base venue analysis
            base_analysis = self.get_player_venue_performance(player_name, venue_name, seasons)
            
            if base_analysis.get('error'):
                return base_analysis
            
            # Enhance with advanced analytics
            advanced_analysis = {
                **base_analysis,
                'advanced_metrics': {},
                'pitch_level_analysis': {},
                'game_by_game_breakdown': {},
                'performance_trends': {}
            }
            
            player_id = base_analysis['player']['id']
            venue_id = base_analysis['venue']['id']
            
            # Get detailed game analysis for games at this venue
            venue_games = []
            for season in seasons:
                try:
                    # Get games at venue
                    start_date = f"{season}-03-01"
                    end_date = f"{season}-11-30"
                    
                    schedule = self.get_schedule(start_date, end_date)
                    
                    if 'dates' in schedule:
                        for date_info in schedule['dates']:
                            for game in date_info.get('games', []):
                                if game.get('venue', {}).get('id') == venue_id:
                                    # Check if player's team was involved
                                    home_team = game.get('teams', {}).get('home', {}).get('team', {})
                                    away_team = game.get('teams', {}).get('away', {}).get('team', {})
                                    
                                    # For now, assume player could be on either team
                                    game_id = game.get('gamePk')
                                    
                                    if include_pitch_analysis:
                                        # Get pitch-level analysis
                                        pitch_data = self.get_game_pitch_data(game_id)
                                        game_events = self.get_game_events(game_id)
                                        
                                        # Filter for this player
                                        player_pitches = pitch_data.get('pitches_by_batter', {}).get(str(player_id), [])
                                        player_events = [
                                            event for event in game_events.get('all_events', [])
                                            if event.get('batter', {}).get('id') == player_id
                                        ]
                                        
                                        if player_pitches or player_events:
                                            venue_games.append({
                                                'game_id': game_id,
                                                'date': game.get('gameDate'),
                                                'opponent': away_team.get('name') if home_team.get('name') else home_team.get('name'),
                                                'pitches_faced': len(player_pitches),
                                                'events': len(player_events),
                                                'pitch_details': player_pitches[:10],  # Sample
                                                'event_details': player_events
                                            })
                
                except Exception as e:
                    logger.warning(f"Could not analyze games for season {season}: {e}")
            
            advanced_analysis['game_by_game_breakdown'] = venue_games
            
            # Get situational stats for comparison
            for season in seasons:
                try:
                    situational = self.get_player_situational_stats(player_id, season)
                    advanced_analysis['advanced_metrics'][f'season_{season}_situations'] = situational
                except Exception as e:
                    logger.warning(f"Could not get situational stats for {season}: {e}")
            
            # Summary metrics
            total_venue_pitches = sum(game.get('pitches_faced', 0) for game in venue_games)
            total_venue_events = sum(game.get('events', 0) for game in venue_games)
            
            advanced_analysis['performance_trends'] = {
                'total_games_analyzed': len(venue_games),
                'total_pitches_tracked': total_venue_pitches,
                'total_plate_appearances': total_venue_events,
                'analysis_depth': 'comprehensive_with_pitch_data' if include_pitch_analysis else 'standard',
                'data_availability': 'excellent' if venue_games else 'limited'
            }
            
            return advanced_analysis
            
        except Exception as e:
            logger.error(f"Error in advanced venue analysis: {e}")
            return {'error': f"Advanced analysis failed: {str(e)}"}
    
    def get_comprehensive_game_data(self, game_id: int) -> Dict:
        """Get all available game data including play-by-play and pitch data"""
        hydrate_params = [
            'venue', 'team', 'linescore', 'boxscore', 'plays', 'playByPlay',
            'probablePitcher', 'weather', 'officials', 'broadcasts', 'decisions',
            'person', 'stats', 'highlights', 'review', 'flags'
        ]
        
        params = {'hydrate': ','.join(hydrate_params)}
        return self._make_request(f'game/{game_id}', params)
    
    def get_games_advanced_filter(self, **filters) -> Dict:
        """
        Advanced game filtering by multiple criteria
        Supports: team, venue, player, date range, game type, etc.
        """
        base_params = {
            'sportId': 1,
            'hydrate': 'team,venue,linescore'
        }
        
        # Map common filter names to API parameters
        param_mapping = {
            'team_id': 'teamId',
            'venue_id': 'venueIds',
            'start_date': 'startDate',
            'end_date': 'endDate',
            'season': 'season',
            'game_type': 'gameType'
        }
        
        for filter_key, filter_value in filters.items():
            if filter_key in param_mapping:
                base_params[param_mapping[filter_key]] = filter_value
        
        return self._make_request('schedule', base_params)
