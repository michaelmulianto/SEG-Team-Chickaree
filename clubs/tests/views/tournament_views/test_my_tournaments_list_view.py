"""Test view for accessing list of tournaments linked to currently logged in user."""

from django.test import TestCase
from django.urls import reverse

from clubs.models import User

class MyTournamentListViewTestCase(TestCase):
    """Test all validation within view my tournaments list"""
    
    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_user.json', 
    'clubs/tests/fixtures/default_tournament.json',
    'clubs/tests/fixtures/other_clubs.json',
    'clubs/tests/fixtures/other_tournaments.json',
    ]
    
    def setUp(self):
        self.user = User.objects.get(username='johndoe')