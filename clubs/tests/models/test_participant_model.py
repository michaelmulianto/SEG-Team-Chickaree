"""Tests for participant model"""

from django.test import TestCase
from clubs.models import Organiser, Club, Participant, User, Membership, Tournament, MemberTournamentRelationship
from django.core.exceptions import ValidationError

class ParticipantModelTestCase(TestCase):
    """Tests all model level validation of a participant of a tournament"""

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

        self.participant = Participant.objects.create(
            round_eliminated = 1,

            #values for MemberTournamentRelationship
            member = self.first_membership,
            tournament = self.first_tournament
        )


    def test_valid_participant(self):
        self._assert_participant_is_valid()

    # round eliminated field test
    def test_round_eliminated_cannot_be_blank(self):
        self.participant.round_eliminated = None
        self._assert_participant_is_invalid()

    def test_round_eliminated_attribute_for_participant_must_be_integer(self):
        self.participant.round_eliminated = "WRONG INPUT"
        self._assert_participant_is_invalid()

    # joined field test
    def test_joined_attribute_for_participant_must_be_datetime(self):
        self.participant.joined = "WRONG INPUT"
        self._assert_participant_is_invalid()

    def test_a_member_can_participate_in_more_than_one_tournament(self):
        try:
            Participant.objects.create(
                member = self.second_membership,
                tournament = self.first_tournament,
                round_eliminated = 1
            )
        except(ValidationError):
            self.fail("A member should be able to participate in more than one tournament")

    def test_there_can_be_more_than_one_participant_model(self):
        try:
            Participant.objects.create(
                member = self.second_membership,
                tournament = self.second_tournament
            )
        except(ValidationError):
            self.fail('We should be able to have more than one organiser')

    def test_there_can_be_more_than_one_participant_in_a_single_tournament(self):
        try:
            Participant.objects.create(
                member = self.second_membership,
                tournament = self.first_tournament,
                round_eliminated = 1
            )
        except(ValidationError):
            self.fail('We should be able to have more than one organiser')

    def test_round_eliminated_for_participant_is_minus_1_by_default(self):
        other_participant = Participant.objects.create(
                                member = self.first_membership,
                                tournament = self.second_tournament,
                                )
        self.assertEqual(other_participant.round_eliminated, -1)

    def test_we_can_get_the_member_from_the_MemberTournamentRelations_object_from_participant_model(self):
        self.assertEqual(self.participant.member, self.first_membership)

    def test_we_can_get_the_tournament_from_the_MemberTournamentRelations_object_from_participant_model(self):
        self.assertEqual(self.participant.tournament, self.first_tournament)

    def test_deleting_the_participant_model_does_not_cause_errors(self):
        self.participant.delete()

    def test_creating_a_new_participant_shows_joined_field_after_older_participants(self):
        new_participant = Participant.objects.create(
                member = self.second_membership,
                tournament = self.first_tournament,
                round_eliminated = 1
            )
        self.assertLess(self.participant.joined, new_participant.joined)

    # test string
    def test_str(self):
        self.assertEqual(self.participant.__str__(), f'{self.first_membership.user.first_name} {self.first_membership.user.last_name} in {self.first_tournament.name} by {self.first_tournament.club}')

    #Assertions
    def _assert_participant_is_valid(self):
        try:
            self.participant.full_clean()
        except(ValidationError):
            self.fail('Test Organiser should be valid')

    def _assert_participant_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.participant.full_clean()
