from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from apps.teams.models import Team
from apps.players.models import Player
from apps.games.models import Game
import json

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def natural_language_search(request):
    """
    Natural language search endpoint that searches across teams, players, and games
    """
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip().lower()
        
        if not query:
            return Response(
                {'error': 'Query parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'teams': [],
            'players': [],
            'games': []
        }
        
        # Search teams by name, location, or abbreviation
        teams = Team.objects.filter(
            Q(name__icontains=query) |
            Q(location_name__icontains=query) |
            Q(team_name__icontains=query) |
            Q(abbreviation__icontains=query)
        )[:10]
        
        for team in teams:
            results['teams'].append({
                'id': team.id,
                'name': team.name,
                'location_name': team.location_name,
                'team_name': team.team_name,
                'abbreviation': team.abbreviation,
                'type': 'team'
            })
        
        # Search players by name
        players = Player.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(full_name__icontains=query)
        )[:10]
        
        for player in players:
            results['players'].append({
                'id': player.id,
                'name': player.full_name,
                'position': getattr(player, 'primary_position', 'Unknown'),
                'team': getattr(player.current_team, 'name', 'Free Agent') if hasattr(player, 'current_team') and player.current_team else 'Free Agent',
                'type': 'player'
            })
        
        # Search games by team names or date
        games = Game.objects.filter(
            Q(home_team__name__icontains=query) |
            Q(away_team__name__icontains=query)
        )[:10]
        
        for game in games:
            results['games'].append({
                'id': game.id,
                'home_team': game.home_team.name if game.home_team else 'TBD',
                'away_team': game.away_team.name if game.away_team else 'TBD',
                'game_date': game.game_date.isoformat() if hasattr(game, 'game_date') and game.game_date else None,
                'status': getattr(game, 'status', 'Unknown'),
                'type': 'game'
            })
        
        return Response(results, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Search failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
