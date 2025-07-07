import pytest
from django.urls import reverse
from rest_framework import status
from .factories import PlayerFactory

@pytest.mark.django_db
class TestPlayerViewSet:

    def test_list_players(self, client):
        PlayerFactory.create_batch(5)
        response = client.get(reverse('players-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_create_player(self, client):
        data = {
            'name': 'Test Player',
            'team': 'Test Team',
            'position': 'Pitcher',
            'batting_average': 0.250,
            'era': 3.50
        }
        response = client.post(reverse('players-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']

    def test_retrieve_player(self, client):
        player = PlayerFactory()
        response = client.get(reverse('players-detail', args=[player.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == player.name

    def test_update_player(self, client):
        player = PlayerFactory()
        data = {
            'name': 'Updated Player',
            'team': player.team,
            'position': player.position,
            'batting_average': 0.300,
            'era': 2.75
        }
        response = client.put(reverse('players-detail', args=[player.id]), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == data['name']

    def test_delete_player(self, client):
        player = PlayerFactory()
        response = client.delete(reverse('players-detail', args=[player.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None

    def test_invalid_player_creation(self, client):
        data = {
            'name': '',
            'team': 'Test Team',
            'position': 'Pitcher',
            'batting_average': 0.250,
            'era': 3.50
        }
        response = client.post(reverse('players-list'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data.keys()