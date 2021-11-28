"""Test view to fetch info about a specific club."""

from django.test import TestCase
from django.urls import reverse
from clubs.tests.helpers import reverse_with_next
from clubs.models import Club, User

class ShowClubTest(TestCase):
    """Test aspects of show club view."""

    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.club = Club.objects.get(name='King\'s Knights')
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('show_club', kwargs={'club_id': self.club.id})

    def test_show_club_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}')

    def test_show_club_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_club_with_invalid_club_id(self):
        self.url = reverse('show_club', kwargs={'club_id': self.club.id-1})
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_get_show_club_with_valid_id(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'show_club.html')
