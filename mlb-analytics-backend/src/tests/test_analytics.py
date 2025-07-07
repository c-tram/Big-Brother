import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.analytics.models import Analytics

@pytest.mark.django_db
class TestAnalyticsAPI:
    def setup_method(self):
        self.client = APIClient()
        self.analytics_data = {
            'metric_name': 'example_metric',
            'value': 100,
            'timestamp': '2023-01-01T00:00:00Z'
        }
        self.analytics_instance = Analytics.objects.create(**self.analytics_data)

    def test_get_analytics_list(self):
        response = self.client.get(reverse('analytics-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_create_analytics(self):
        response = self.client.post(reverse('analytics-list'), self.analytics_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Analytics.objects.count() == 2  # One from setup and one created

    def test_get_analytics_detail(self):
        response = self.client.get(reverse('analytics-detail', args=[self.analytics_instance.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['metric_name'] == self.analytics_data['metric_name']

    def test_update_analytics(self):
        updated_data = {'metric_name': 'updated_metric', 'value': 200}
        response = self.client.put(reverse('analytics-detail', args=[self.analytics_instance.id]), updated_data)
        assert response.status_code == status.HTTP_200_OK
        self.analytics_instance.refresh_from_db()
        assert self.analytics_instance.metric_name == updated_data['metric_name']

    def test_delete_analytics(self):
        response = self.client.delete(reverse('analytics-detail', args=[self.analytics_instance.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Analytics.objects.count() == 0  # Ensure it has been deleted