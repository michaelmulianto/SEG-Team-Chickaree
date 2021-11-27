"""Test view to fetch info about a specific club."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club

class ShowClubTest(TestCase):
    """Test aspects of show club view"""

    def setUp(self):
        self.club = Club.objects.create(
            name = 'Kings Knight',
            location = 'Kings College',
            description = 'Best club in the world'
        )
        self.url = reverse('show_club', kwargs={'club_id': self.club.id})

    def test_show_club_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}')

    def test_get_show_club_with_valid_id(self):
        pass

    def test_get_show_club_with_invalid_id(self):
        pass
