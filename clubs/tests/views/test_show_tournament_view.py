"""Test view to fetch info about a specific tournament."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, Membership, User
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin

class ShowClubViewTestCase(TestCase, MenuTesterMixin):
    """Test aspects of show tournament view"""

    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.club = Club.objects.get(name='King\'s Knights')
        self.url = reverse('show_tournament', kwargs={'tournament_id': self.tournament.id})
        self.member = Membership.objects.create(
            user = User.objects.get(username='johndoe'),
            club = self.club,
            is_owner = True,
            is_officer = False
        )

    def test_show_tournament_url(self):
        self.assertEqual(self.url, f'/tournament/{self.tournament.id}/')


    def test_get_show_tournament_with_valid_id(self):
        self.client.login(email="johndoe@example.org", password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "show_tournament.html")
        self.assertEqual(response.status_code, 200) #OK
        self.assert_menu(response)

    def test_promote_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_tournament_with_invalid_id(self):
        self.client.login(email="johndoe@example.org", password="Password123")
        self.url = reverse('show_tournament', kwargs={'tournament_id': self.tournament.id-1})
        response = self.client.get(self.url)
        redirect_url = reverse("show_tournaments")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
