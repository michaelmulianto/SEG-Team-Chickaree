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
        self.owner_user = User.objects.get(username='johndoe')
        self.officer_user = User.objects.get(username='jamiedoe')
        self.second_officer_user = User.objects.get(username='tomdoe')
        self.non_member_user = User.objects.get(username='janedoe')
        self.participant_user = User.objects.get(username='richarddoe')

        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
        )

        self.officer_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_officer = True,
        )

        self.participant_member = Membership.objects.create(
            user = self.participant_user,
            club = self.club,
        )

        self.tournament = Tournament.objects.get(name="Grand Championship")

        self.lead_organiser = Organiser.objects.create(
            member = self.owner_member,
            tournament = self.tournament,
            is_lead_organiser = True
        )

        self.standard_organiser = Organiser.objects.create(
            member = self.officer_member,
            tournament = self.tournament,
        )

        self.participant = Participant.objects.create(
            member = self.participant_member,
            tournament = self.tournament
        )

        self.url = reverse('add_tournament_organiser_list', kwargs={'tournament_id': self.tournament.id})
