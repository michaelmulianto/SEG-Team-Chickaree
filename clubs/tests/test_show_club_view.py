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
            description = 'best club in the world'
        )
        self.url = reverse('show_club', kwargs={'club_id': self.club.id})

    def test_show_club_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}')

    def test_get_show_club_with_valid_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertContains(response, "Kings Knight")
        self.assertContains(response, "Kings College")
        self.assertContains(response, "best club in the world")

    def test_get_show_club_with_invalid_id(self):
        url = reverse('show_club', kwargs={'club_id': self.club.id+1})
        response = self.client.get(url, follow=True)
        response_url = reverse('show_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
