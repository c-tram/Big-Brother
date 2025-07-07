from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from services.mlb_api import MLBApi, MLBApiError
from apps.teams.models import Team, TeamSeason, League, Division, Venue
from apps.players.models import Player, PlayerSeason, PitcherSeason
from apps.games.models import Game, GameLineScore, GamePlayerStats

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def sync_teams_from_mlb(self):
    """Sync all MLB teams from the API"""
    try:
        mlb_api = MLBApi()
        teams_data = mlb_api.get_teams()
        
        synced_count = 0
        
        for team_data in teams_data.get('teams', []):
            team, created = Team.objects.update_or_create(
                mlb_id=team_data.get('id'),
                defaults={
                    'name': team_data.get('name', ''),
                    'team_name': team_data.get('teamName', ''),
                    'location_name': team_data.get('locationName', ''),
                    'abbreviation': team_data.get('abbreviation', ''),
                    'team_code': team_data.get('teamCode', ''),
                    'file_code': team_data.get('fileCode', ''),
                    'club_name': team_data.get('clubName', ''),
                    'short_name': team_data.get('shortName', ''),
                    'franchise_name': team_data.get('franchiseName', ''),
                    'first_year_of_play': team_data.get('firstYearOfPlay'),
                    'active': team_data.get('active', True),
                }
            )
            
            # Update league and division info
            if 'league' in team_data:
                league_data = team_data['league']
                league, _ = League.objects.update_or_create(
                    mlb_id=league_data.get('id'),
                    defaults={
                        'name': league_data.get('name', ''),
                        'abbreviation': league_data.get('abbreviation', ''),
                        'name_short': league_data.get('nameShort', ''),
                    }
                )
                team.league = league
            
            if 'division' in team_data:
                division_data = team_data['division']
                division, _ = Division.objects.update_or_create(
                    mlb_id=division_data.get('id'),
                    defaults={
                        'name': division_data.get('name', ''),
                        'name_short': division_data.get('nameShort', ''),
                        'abbreviation': division_data.get('abbreviation', ''),
                        'league': league if 'league' in team_data else None,
                    }
                )
                team.division = division
            
            # Update venue info
            if 'venue' in team_data:
                venue_data = team_data['venue']
                venue, _ = Venue.objects.update_or_create(
                    mlb_id=venue_data.get('id'),
                    defaults={
                        'name': venue_data.get('name', ''),
                        'city': venue_data.get('city', ''),
                        'state': venue_data.get('state', ''),
                        'country': venue_data.get('country', 'USA'),
                        'active': venue_data.get('active', True),
                    }
                )
                team.venue = venue
            
            team.save()
            synced_count += 1
            
            if created:
                logger.info(f"Created new team: {team}")
            else:
                logger.info(f"Updated team: {team}")
        
        logger.info(f"Successfully synced {synced_count} teams")
        return {"success": True, "synced_count": synced_count}
        
    except MLBApiError as e:
        logger.error(f"MLB API error in sync_teams_from_mlb: {str(e)}")
        raise self.retry(countdown=60, exc=e)
    except Exception as e:
        logger.error(f"Unexpected error in sync_teams_from_mlb: {str(e)}")
        raise self.retry(countdown=60, exc=e)

@shared_task(bind=True, max_retries=3)
def sync_team_standings(self, season=None):
    """Sync team standings for a given season"""
    try:
        mlb_api = MLBApi()
        
        if season is None:
            season = mlb_api.get_current_season()
        
        standings_data = mlb_api.get_standings(season=season)
        
        synced_count = 0
        
        for record in standings_data.get('records', []):
            for team_record in record.get('teamRecords', []):
                team_data = team_record.get('team', {})
                
                try:
                    team = Team.objects.get(mlb_id=team_data.get('id'))
                    
                    team_season, created = TeamSeason.objects.update_or_create(
                        team=team,
                        season=season,
                        defaults={
                            'wins': team_record.get('wins', 0),
                            'losses': team_record.get('losses', 0),
                            'games_played': team_record.get('gamesPlayed', 0),
                            'runs_scored': team_record.get('runsScored', 0),
                            'runs_allowed': team_record.get('runsAllowed', 0),
                            'division_rank': team_record.get('divisionRank'),
                            'league_rank': team_record.get('leagueRank'),
                            'wild_card_rank': team_record.get('wildCardRank'),
                            'games_back': team_record.get('gamesBack', 0),
                            'wild_card_games_back': team_record.get('wildCardGamesBack', 0),
                            'elimination_number': team_record.get('eliminationNumber'),
                            'magic_number': team_record.get('magicNumber'),
                        }
                    )
                    
                    # Parse streak information
                    streak_code = team_record.get('streak', {}).get('streakCode', '')
                    if streak_code.startswith('W'):
                        team_season.streak_type = 'W'
                        team_season.streak_number = int(streak_code[1:]) if len(streak_code) > 1 else 0
                    elif streak_code.startswith('L'):
                        team_season.streak_type = 'L'
                        team_season.streak_number = int(streak_code[1:]) if len(streak_code) > 1 else 0
                    
                    team_season.save()
                    synced_count += 1
                    
                except Team.DoesNotExist:
                    logger.warning(f"Team with MLB ID {team_data.get('id')} not found")
                    continue
        
        logger.info(f"Successfully synced standings for {synced_count} teams in {season}")
        return {"success": True, "synced_count": synced_count, "season": season}
        
    except MLBApiError as e:
        logger.error(f"MLB API error in sync_team_standings: {str(e)}")
        raise self.retry(countdown=60, exc=e)
    except Exception as e:
        logger.error(f"Unexpected error in sync_team_standings: {str(e)}")
        raise self.retry(countdown=60, exc=e)

@shared_task(bind=True, max_retries=3)
def sync_games_by_date(self, date_str):
    """Sync games for a specific date"""
    try:
        mlb_api = MLBApi()
        games_data = mlb_api.get_games_by_date(date_str)
        
        synced_count = 0
        
        for game_data in games_data.get('dates', []):
            for game in game_data.get('games', []):
                
                # Get teams
                try:
                    home_team = Team.objects.get(mlb_id=game['teams']['home']['team']['id'])
                    away_team = Team.objects.get(mlb_id=game['teams']['away']['team']['id'])
                except Team.DoesNotExist as e:
                    logger.warning(f"Team not found for game {game.get('gamePk')}: {str(e)}")
                    continue
                
                # Get venue
                venue = None
                if 'venue' in game:
                    try:
                        venue = Venue.objects.get(mlb_id=game['venue']['id'])
                    except Venue.DoesNotExist:
                        pass
                
                # Create or update game
                game_obj, created = Game.objects.update_or_create(
                    mlb_game_pk=game.get('gamePk'),
                    defaults={
                        'game_guid': game.get('gameGuid', ''),
                        'game_date': datetime.strptime(game.get('gameDate', ''), '%Y-%m-%dT%H:%M:%SZ').date(),
                        'game_datetime': datetime.strptime(game.get('gameDate', ''), '%Y-%m-%dT%H:%M:%SZ'),
                        'home_team': home_team,
                        'away_team': away_team,
                        'venue': venue,
                        'season': game.get('season'),
                        'season_type': game.get('seasonType', 'Regular Season'),
                        'status': game.get('status', {}).get('codedGameState', 'scheduled'),
                        'detailed_state': game.get('status', {}).get('detailedState', ''),
                        'current_inning': game.get('linescore', {}).get('currentInning'),
                        'inning_state': game.get('linescore', {}).get('inningState', ''),
                        'day_night': game.get('dayNight', ''),
                    }
                )
                
                # Update scores if game is final
                if game.get('status', {}).get('codedGameState') == 'final':
                    linescore = game.get('linescore', {})
                    game_obj.home_score = linescore.get('teams', {}).get('home', {}).get('runs')
                    game_obj.away_score = linescore.get('teams', {}).get('away', {}).get('runs')
                    game_obj.save()
                
                synced_count += 1
                
                if created:
                    logger.info(f"Created new game: {game_obj}")
                else:
                    logger.info(f"Updated game: {game_obj}")
        
        logger.info(f"Successfully synced {synced_count} games for {date_str}")
        return {"success": True, "synced_count": synced_count, "date": date_str}
        
    except MLBApiError as e:
        logger.error(f"MLB API error in sync_games_by_date: {str(e)}")
        raise self.retry(countdown=60, exc=e)
    except Exception as e:
        logger.error(f"Unexpected error in sync_games_by_date: {str(e)}")
        raise self.retry(countdown=60, exc=e)

@shared_task(bind=True, max_retries=3)
def sync_team_roster(self, team_id, season=None):
    """Sync roster for a specific team"""
    try:
        mlb_api = MLBApi()
        
        if season is None:
            season = mlb_api.get_current_season()
        
        team = Team.objects.get(mlb_id=team_id)
        roster_data = mlb_api.get_team_roster(team_id, season)
        
        synced_count = 0
        
        for player_data in roster_data.get('roster', []):
            person_data = player_data.get('person', {})
            
            player, created = Player.objects.update_or_create(
                mlb_id=person_data.get('id'),
                defaults={
                    'first_name': person_data.get('firstName', ''),
                    'last_name': person_data.get('lastName', ''),
                    'full_name': person_data.get('fullName', ''),
                    'birth_date': person_data.get('birthDate'),
                    'birth_city': person_data.get('birthCity', ''),
                    'birth_state_province': person_data.get('birthStateProvince', ''),
                    'birth_country': person_data.get('birthCountry', ''),
                    'height': person_data.get('height', ''),
                    'weight': person_data.get('weight'),
                    'primary_position': player_data.get('position', {}).get('abbreviation', ''),
                    'bat_side': person_data.get('batSide', {}).get('code', ''),
                    'pitch_hand': person_data.get('pitchHand', {}).get('code', ''),
                    'mlb_debut_date': person_data.get('mlbDebutDate'),
                    'current_team': team,
                    'active': person_data.get('active', True),
                }
            )
            
            synced_count += 1
            
            if created:
                logger.info(f"Created new player: {player}")
            else:
                logger.info(f"Updated player: {player}")
        
        logger.info(f"Successfully synced {synced_count} players for {team}")
        return {"success": True, "synced_count": synced_count, "team": str(team)}
        
    except Team.DoesNotExist:
        logger.error(f"Team with MLB ID {team_id} not found")
        return {"success": False, "error": "Team not found"}
    except MLBApiError as e:
        logger.error(f"MLB API error in sync_team_roster: {str(e)}")
        raise self.retry(countdown=60, exc=e)
    except Exception as e:
        logger.error(f"Unexpected error in sync_team_roster: {str(e)}")
        raise self.retry(countdown=60, exc=e)

@shared_task
def daily_data_sync():
    """Daily task to sync MLB data"""
    logger.info("Starting daily MLB data sync")
    
    # Sync teams (less frequent)
    sync_teams_from_mlb.delay()
    
    # Sync current season standings
    sync_team_standings.delay()
    
    # Sync games for today
    today = datetime.now().strftime('%Y-%m-%d')
    sync_games_by_date.delay(today)
    
    # Sync games for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    sync_games_by_date.delay(tomorrow)
    
    logger.info("Daily MLB data sync tasks queued")

@shared_task
def weekly_data_sync():
    """Weekly task to sync comprehensive MLB data"""
    logger.info("Starting weekly MLB data sync")
    
    # Sync all team rosters
    teams = Team.objects.filter(active=True)
    for team in teams:
        sync_team_roster.delay(team.mlb_id)
    
    # Sync last week's games
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        sync_games_by_date.delay(date)
    
    logger.info("Weekly MLB data sync tasks queued")
