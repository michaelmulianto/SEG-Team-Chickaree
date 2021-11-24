"""Test user-facing implementation of the sign up form."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club
from django.contrib.auth.hashers import check_password
from clubs.tests.helpers import LogInTester

class ClubDetailsViewTestCase(TestCase, LogInTester):
    def setUp(self):
        self.club = Club.objects.create(
            name = 'Kings Knight',
            location = 'Kings College',
            description = 'best club in the world'
        )
        self.url = reverse('club_details', kwargs={'club_id': self.club.id})

    def test_club_details_url(self):
        self.assertEqual(self.url, f'/club_details/{self.club.id}')

    def test_get_show_club_with_valid_id(self):
        pass
