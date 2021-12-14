"""Test view to fetch participant list of a specific tournament."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, Membership, User, Tournament, Organiser, Participant
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin

class ShowClubViewTestCase(TestCase, MenuTesterMixin):
    """Test aspects of show tournament participants view"""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_tournament.json',
    ]

    def setUp(self):
        self.owner_user = User.objects.get(username='johndoe')
        self.non_member_user = User.objects.get(username='janedoe')
        self.participant_user = User.objects.get(username='richarddoe')

        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
        )

        self.participant_member = {
            user = self.participant_user,
            club = self.club,
        }

        self.tournament = Tournament.objects.get(name="Grand Championship")

        self.organiser = Organiser.objects.create(
            member = self.owner_member,
            tournament = self.tournament,
            is_lead_organiser = True
        )

        self.participant = Participant.objects.create(
            member = self.participant_member,
            tournament = self.tournament
        )

        self.url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id})
