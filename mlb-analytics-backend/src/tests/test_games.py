from django.test import TestCase
from apps.games.models import Game
from rest_framework import status
from rest_framework.test import APIClient

class GameModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.game = Game.objects.create(
            home_team='Team A',
            away_team='Team B',
            home_score=5,
            away_score=3,
            date='2023-10-01'
        )

    def test_game_creation(self):
        self.assertEqual(self.game.home_team, 'Team A')
        self.assertEqual(self.game.away_team, 'Team B')
        self.assertEqual(self.game.home_score, 5)
        self.assertEqual(self.game.away_score, 3)

    def test_get_game(self):
        response = self.client.get(f'/api/games/{self.game.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['home_team'], 'Team A')

    def test_update_game(self):
        response = self.client.patch(f'/api/games/{self.game.id}/', {'home_score': 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.game.refresh_from_db()
        self.assertEqual(self.game.home_score, 6)

    def test_delete_game(self):
        response = self.client.delete(f'/api/games/{self.game.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Game.objects.filter(id=self.game.id).exists())