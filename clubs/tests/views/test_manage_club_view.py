"""Test view to fetch info about a specific club."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, Member, User
from clubs.tests.helpers import reverse_with_next

class ShowClubViewTestCase(TestCase):
    """Test aspects of show club view"""

    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.club = Club.objects.get(name='King\'s Knights')
        self.url = reverse('manage_club', kwargs={'club_id': self.club.id})
        self.member = Member.objects.create(
            user = User.objects.get(username='johndoe'),
            club = self.club,
            is_owner = True,
            is_officer = False
        )

    def test_manage_club_url(self):
        self.assertEqual(self.url,f'/manage_club/{self.club.id}')

    def test_get_manage_club_with_valid_id(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "manage_club.html")
        self.assertEqual(response.status_code, 200) #OK

    def test_promote_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_manage_club_with_invalid_id(self):
        self.client.login(username="johndoe", password="Password123")
        self.url = reverse('manage_club', kwargs={'club_id': self.club.id-1})
        response = self.client.get(self.url)
        redirect_url = reverse("show_clubs")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
