"""Test view to fetch a list of candidates to be added as organisers of a certain tournament, only visible by the lead organiser."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, Membership, User, Tournament, Organiser, Participant
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin

class AddTournamentOrganiserListViewTestCase(TestCase, MenuTesterMixin):
    """Test aspects of show tournament participants view"""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_tournament.json',
    ]

    def setUp(self):
        self.lead_organiser_user = User.objects.get(username='johndoe')
        self.standard_organiser_user = User.objects.get(username='richarddoe')
        self.officer_organiser_candidate_user = User.objects.get(username='jamiedoe')
        self.non_member_user = User.objects.get(username='janedoe')

        self.club = Club.objects.get(name='King\'s Knights')

        self.lead_organiser_member = Membership.objects.create(
            club = self.club,
            user = self.lead_organiser_user,
            is_owner = True,
        )

        self.standard_organiser_member = Membership.objects.create(
            club = self.club,
            user = self.standard_organiser_user,
            is_officer = True,
        )

        self.officer_organiser_candidate_member = Membership.objects.create(
            club = self.club,
            user = self.officer_organiser_candidate_user,
            is_officer = True,
        )

        self.tournament = Tournament.objects.get(name="Grand Championship")

        self.lead_organiser = Organiser.objects.create(
            member = self.lead_organiser_member,
            tournament = self.tournament,
            is_lead_organiser = True
        )

        self.standard_organiser = Organiser.objects.create(
            member = self.standard_organiser_member,
            tournament = self.tournament,
        )

        self.url = reverse('add_tournament_organiser_list', kwargs={'tournament_id': self.tournament.id})


    def test_get_add_tournament_organiser_list_url(self):
        self.assertEqual(self.url, f'/tournament/{self.tournament.id}/add_organiser/')

    def test_get_add_tournament_organiser_list_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_tournament_organiser_list_with_invalid_id(self):
        self.client.login(email=self.lead_organiser_user.email, password="Password123")
        self.url = reverse('add_tournament_organiser_list', kwargs={'tournament_id': 999})
        response = self.client.get(self.url)
        redirect_url = reverse("show_clubs")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_tournament_organiser_list_redirects_when_not_member(self):
        self.client.login(email=self.non_member_user.email, password="Password123")
        response = self.client.get(self.url)
        redirect_url = reverse("show_club", kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_tournament_organiser_list_redirects_not_lead_organiser(self):
        self.client.login(email=self.standard_organiser_user.email, password="Password123")
        response = self.client.get(self.url)
        redirect_url = reverse("show_tournament", kwargs={'tournament_id': self.tournament.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_tournament_organiser_list_with_valid_id(self):
        self.client.login(email=self.lead_organiser_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, "tournament/add_tournament_organiser_list.html")
        self.assert_menu(response)
