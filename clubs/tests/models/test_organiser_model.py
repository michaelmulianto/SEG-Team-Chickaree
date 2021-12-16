"""Test for Organiser model"""

from django.test import TestCase
from clubs.models import Organiser, Club, User, Membership, Tournament, MemberTournamentRelationship
from django.core.exceptions import ValidationError

class OrganiserModelTestCase(TestCase):
    """Tests all model level validation of an organiser of a tournament"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_tournament.json',
        'clubs/tests/fixtures/other_tournaments.json']

    def setUp(self):

        self.club = Club.objects.get(name = "King\'s Knights")

        self.first_user = User.objects.get(username = "johndoe")
        self.second_user = User.objects.get(username = "janedoe")

        self.first_membership = Membership.objects.create(
            user = self.first_user,
            club = self.club
        )
        self.second_membership = Membership.objects.create(
            user = self.second_user,
            club = self.club
        )

        self.first_tournament = Tournament.objects.get(name = 'Grand Championship')
        self.second_tournament = Tournament.objects.get(name = 'Just A League')

        self.organiser = Organiser.objects.create(
            is_lead_organiser = True,
            #values for MemberTournamentRelationship
            member = self.first_membership,
            tournament = self.first_tournament
        )


    def test_valid_Organiser(self):
        self._assert_organiser_is_valid()

    # is organiser field test
    def test_is_lead_organiser_cannot_be_blank(self):
        self.organiser.is_lead_organiser = None
        self._assert_organiser_is_invalid()

    def test_is_lead_organiser_must_be_boolean(self):
        self.organiser.is_lead_organiser = "WRONG INPUT"
        self._assert_organiser_is_invalid()

    def test_a_member_can_organise_more_than_one_tournament(self):
        try:
            Organiser.objects.create(
                member = self.second_membership,
                tournament = self.first_tournament,
                is_lead_organiser = True
            )
        except(ValidationError):
            self.fail("A member should be able to organise more than one tournament")

    def test_there_can_be_more_than_one_organiser_model(self):
        try:
            Organiser.objects.create(
                member = self.second_membership,
                tournament = self.second_tournament
            )
        except(ValidationError):
            self.fail('We should be able to have more than one organiser')

    def test_there_can_be_more_than_one_organiser(self):
        try:
            Organiser.objects.create(
                member = self.second_membership,
                tournament = self.first_tournament,
                is_lead_organiser = True
            )
        except(ValidationError):
            self.fail('We should be able to have more than one organiser')

    def test_is_lead_organiser_is_false_by_default(self):
        other_organiser = Organiser.objects.create(
                            member = self.first_membership,
                            tournament = self.second_tournament,
                            )
        self.assertFalse(other_organiser.is_lead_organiser)

    def test_we_can_get_the_member_from_the_MemberTournamentRelations_object_from_Organiser_model(self):
        self.assertEqual(self.organiser.member, self.first_membership)

    def test_we_can_get_the_tournament_from_the_MemberTournamentRelations_object_from_Organiser_model(self):
        self.assertEqual(self.organiser.tournament, self.first_tournament)

    def test_deleting_the_organiser_model_does_not_cause_errors(self):
        self.organiser.delete()

    #Test string
    def test_str(self):
        self.assertEqual(self.organiser.__str__(), f'{self.first_membership.user.first_name} {self.first_membership.user.last_name} organising {self.first_tournament.name} by {self.first_tournament.club}')


    #Assertions
    def _assert_organiser_is_valid(self):
        try:
            self.organiser.full_clean()
        except(ValidationError):
            self.fail('Test Organiser should be valid')

    def _assert_organiser_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.organiser.full_clean()
