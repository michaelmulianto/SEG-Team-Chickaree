"""Test view for accessing list of tournaments linked to currently logged in user."""

from django.test import TestCase
from django.urls import reverse
from clubs.tests.helpers import reverse_with_next
from datetime import timedelta
from django.utils.timezone import now

from clubs.models import User, Tournament, Participant, Organiser, Membership, Club

class MyTournamentListViewTestCase(TestCase):
    """Test all validation within view my tournaments list"""
    
    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_user.json', 
    'clubs/tests/fixtures/default_tournament.json',
    'clubs/tests/fixtures/other_clubs.json',
    'clubs/tests/fixtures/other_tournaments.json',
    ]
    
    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.t1 = Tournament.objects.get(id=1)
        self.t2 = Tournament.objects.get(id=2)
        self.t3 = Tournament.objects.get(id=3)
        
        self.t2.deadline = now() - timedelta(hours=2)
        self.t2.start = now() - timedelta(hours=1)
        
        self.t3.deadline = now() - timedelta(hours=3)
        self.t3.start = now() - timedelta(hours=2)
        self.t3.end = now() - timedelta(hours=1)
        
        self.member = Membership.objects.create(user=self.user, club=Club.objects.get(id=1))
        
        self.mt_1 = Participant.objects.create(
            member=self.member,
            tournament=self.t1
        )
        self.mt_2 = Participant.objects.create(
            member=self.member,
            tournament=self.t2
        )
        self.mt_3 = Organiser.objects.create(
            member=self.member,
            tournament=self.t3
        )
        
        self.url = reverse('my_tournament_list')
        
    def test_url_is_correct(self):
        self.assertEqual(self.url, '/tournaments/my/')
        
    def test_get_my_tournaments_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    def test_get_my_tournaments_successful_case(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, "tournament/my_tournament_list.html")
        self.assertEqual(response.status_code, 200)
        
    def test_get_my_tournaments_with_no_membertournamentrelationships(self):
        self.mt_1.delete()
        self.mt_2.delete()
        self.mt_3.delete()
        
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, "tournament/my_tournament_list.html")
        self.assertEqual(response.status_code, 200)