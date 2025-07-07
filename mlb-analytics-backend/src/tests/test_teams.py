from django.test import TestCase
from apps.teams.models import Team
from apps.teams.serializers import TeamSerializer

class TeamModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name="New York Yankees",
            city="New York",
            abbreviation="NYY"
        )

    def test_team_creation(self):
        self.assertEqual(self.team.name, "New York Yankees")
        self.assertEqual(self.team.city, "New York")
        self.assertEqual(self.team.abbreviation, "NYY")

class TeamSerializerTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name="Los Angeles Dodgers",
            city="Los Angeles",
            abbreviation="LAD"
        )
        self.serializer = TeamSerializer(instance=self.team)

    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name', 'city', 'abbreviation']))

    def test_serializer_field_values(self):
        data = self.serializer.data
        self.assertEqual(data['name'], self.team.name)
        self.assertEqual(data['city'], self.team.city)
        self.assertEqual(data['abbreviation'], self.team.abbreviation)