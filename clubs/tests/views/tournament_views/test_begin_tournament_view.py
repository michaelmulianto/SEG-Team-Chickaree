"""Tests for view to begin a tournament"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Organiser, User, Club, Tournament, Membership, Participant, Match
from clubs.forms import OrganiseTournamentForm
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.contrib import messages


class BeginTournamentViewTest(TestCase):
    """Test all aspects of the begin tournament view"""

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
            tournament = self.tournament,
            is_lead_organiser = True
        )

        self.data = {
            "result": 1,
        }

        self.url = reverse('begin_tournament', kwargs={'tournament_id': self.tournament.id})

    def test_begin_tournament_url(self):
        self.assertEqual(self.url, f'/tournament/{self.tournament.id}/begin/')
        
    def test_successful_begin_tournament(self):
        self.assertEqual(self.tournament.get_current_round(), None)
        
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        
        self.assertNotEqual(self.tournament.get_current_round(), None)
        self._assert_tournament_page_response(response)
        
    def test_begin_tournament_fails_when_not_member(self):
        self.membership.delete()
        
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        
        self.assertEqual(self.tournament.get_current_round(), None)
        
        # Has different redirect to other cases
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
        
    def test_begin_tournament_fails_when_not_organiser(self):
        self.organiser.delete()
        
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        
        self.assertEqual(self.tournament.get_current_round(), None)
        self._assert_tournament_page_response(response)
        
    def test_begin_tournament_fails_when_already_begun(self):
        premade_round = self.tournament.generate_next_round()
        
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        
        self.assertEqual(self.tournament.get_current_round(), premade_round)
        self._assert_tournament_page_response(response)
        
    # Assertions    
    def _assert_tournament_page_response(self, response):
        response_url = reverse('show_tournament', kwargs={'tournament_id':self.tournament.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_tournament.html')