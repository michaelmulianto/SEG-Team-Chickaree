"""Test backend implementation of the application functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Participant, Membership, Tournament
from clubs.tests.helpers import reverse_with_next

class WithdrawParticipationFromTournamentTestCase(TestCase):
    """Test all aspects of withdrawing participation from a tournament"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_tournament.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.tournament = Tournament.objects.get(name='Grand Championship')
        self.club = Club.objects.get(name="King's Knights")
        self.member = Membership.objects.create(
            user = self.user,
            club = self.club,
            is_officer = False,
            is_owner = False,
        )
        self.participant = Participant.objects.create(
            member = self.member,
            tournament = self.tournament,
        )

        self.url = reverse('withdraw_from_tournament', kwargs = {'tournament_name': self.tournament.name})

    def test_url_of_withdraw_application_to_club(self):
        self.assertEqual(self.url, self.tournament.name + '/withdraw/')
