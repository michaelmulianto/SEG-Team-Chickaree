"""Test view to fetch info about a specific tournament."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, Membership, User, Tournament, Organiser
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin

class ShowClubViewTestCase(TestCase, MenuTesterMixin):
    """Test aspects of show tournament view"""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_tournament.json',
    ]

    def setUp(self):
        self.owner_user = User.objects.get(username='johndoe')
        self.non_member_user = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
        )

        self.tournament = Tournament.objects.get(name="Grand Championship")

        self.organiser = Organiser.objects.create(
            member = self.owner_member,
            tournament = self.tournament
        )


        self.url = reverse('show_tournament', kwargs={'tournament_id': self.club.id})

    def test_show_tournament_url(self):
        self.assertEqual(self.url, f'/tournament/{self.tournament.id}/')

    def test_show_tournament_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_tournament_with_invalid_id(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.url = reverse('show_tournament', kwargs={'tournament_id': self.tournament.id-1})
        response = self.client.get(self.url)
        redirect_url = reverse("show_clubs")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_tournament_redirects_when_not_member(self):
        self.client.login(email=self.non_member_user.email, password="Password123")
        self.url = reverse('show_tournament', kwargs={'tournament_id': self.tournament.id})
        response = self.client.get(self.url)
        redirect_url = reverse("show_club", kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_tournament_with_valid_id(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "show_tournament.html")
        self.assertEqual(response.status_code, 200) #OK
        self.assert_menu(response)
