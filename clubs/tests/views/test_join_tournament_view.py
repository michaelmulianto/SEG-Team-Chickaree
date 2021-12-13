"""Test backend of the create club form."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership, Participant, Tournament
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin


class JoinTournamentViewTest(TestCase, MenuTesterMixin):
    """Test all aspects of the join tournament view"""

    fixtures = ['clubs/tests/fixtures/default_user.json', 'clubs/tests/fixtures/other_clubs.json', 'clubs/tests/fixtures/default_tournament.json', 'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(username = 'johndoe')
        self.club = Club.objects.get(name = "King's Knights")
        self.tournament = Tournament.objects.get(name = 'Grand Championship')
        self.member = Membership.objects.create(
            club = self.club,
            user = self.user
        )

        self.url = reverse('join_tournament', kwargs={'tournament_id': self.tournament.id})

    def test_join_tournament_url(self):
        self.assertEqual(self.url, f'/club/{self.tournament.id}/join_tournament/')

    def test_get_join_tournament_redirects_when_not_logged_in(self):
        response = self.client.post(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_join_tournament(self):
        self.client.login(email=self.user.email, password="Password123")

        # We need to test that participant has been created
        participant_count_before = Participant.objects.count()
        response = self.client.get(self.url, follow=True)
        participant_count_after = Participant.objects.count()

        self.assertEqual(participant_count_after, participant_count_before+1)

    def test_unsuccessful_join_tournament(self):
        self.client.login(email=self.user.email, password='Password123')

        participant_count_before = Participant.objects.count()
        self.member.club = Club.objects.get(name = "Queen's Rooks")
        response = self.client.get(self.url, follow=True)
        participant_count_after = Club.objects.count()

        self.assertEqual(participant_count_after, participant_count_before)
