"""Test backend of the add result view."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Organiser, User, Club, Tournament, Membership, Participant, Match
from clubs.forms import OrganiseTournamentForm
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.contrib import messages


class AddResultViewTest(TestCase, MenuTesterMixin):
    """Test all aspects of the add result view"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
            'clubs/tests/fixtures/default_club.json',
            'clubs/tests/fixtures/default_tournament.json',
            'clubs/tests/fixtures/default_tournament_participants.json'
            ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')
        self.membership = Membership.objects.create(
            club = self.club,
            user=self.user,
            is_officer=True
        )
        
        self.tournament = Tournament.objects.get(id=1)
        self.organiser = Organiser.objects.create(
            member = self.membership,
            tournament = self.tournament
        )

        self.participant_user = Participant.objects.filter(tournament=self.tournament)[0].member.user

        self.data = {
            "result": 1,
        }

        self.match = self.tournament.generate_next_round().get_matches()[0]

        self.url = reverse('add_result', kwargs={'match_id': self.match.id})

    def test_add_result_url(self):
        self.assertEqual(self.url, f'/match/{self.match.id}/add_result/')

    def test_get_add_result_loads_empty_form(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assert_menu(response)
        self.assertEqual(self.match.result, 0)
        self.assertEqual(response.status_code, 200)

    def test_get_add_result_redirects_when_not_logged_in(self):
        response = self.client.post(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_add_result(self):
        self.client.login(email=self.user.email, password="Password123")

        response = self.client.post(self.url, self.data, follow=True)

        self.assertEqual(Match.objects.get(id=self.match.id).result, self.data['result'])

        # Response tests
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
        
    def test_non_organiser_attempts_to_add_result(self):
        self.client.login(email=self.participant_user.email, password='Password123')
    
        response = self.client.post(self.url, self.data, follow=True)

        self.assertEqual(self.match.result, 0)
        
        # Response tests
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
        
    def test_non_member_add_result(self):
        self.client.login(email=self.user.email, password="Password123")
        self.membership.delete()
        
        response = self.client.post(self.url, self.data, follow=True)

        self.assertEqual(Match.objects.get(id=self.match.id).result, 0)

        # Response tests
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
        
    def test_add_result_when_result_already_set(self):
        self.client.login(email=self.user.email, password="Password123")
        self.match.result = 2
        self.match.save()
        
        response = self.client.post(self.url, self.data, follow=True)

        self.assertEqual(Match.objects.get(id=self.match.id).result, 2)

        # Response tests
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
