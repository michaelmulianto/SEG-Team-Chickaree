"""Tests for Club model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Match, Participant, StageInterface, Tournament, Club, User, Membership
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class MatchModelTestCase(TestCase):
    """Test all aspects of a match."""

    fixtures = ['clubs/tests/fixtures/default_user.json','clubs/tests/fixtures/other_users.json','clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/other_clubs.json', 'clubs/tests/fixtures/other_tournaments.json']

    # Test setup
    def setUp(self):
        self.club = Club.objects.get(name="King\'s Knights")

        self.user = User.objects.get(username="johndoe")
        self.second_user = User.objects.get(username="janedoe")

        self.membership = Membership.objects.create(
            user = self.user,
            club = self.club
        )

        self.second_membership = Membership.objects.create(
            user = self.second_user,
            club = self.club
        )

        self.first_par = Participant.objects.create(
            round_eliminated = 1,
            member = self.membership,
            tournament = Tournament.objects.get(name = "Just A League")
        )
        self.second_par = Participant.objects.create(
            round_eliminated = 1,
            member = self.second_membership,
            tournament = Tournament.objects.get(name = "Just A League")
        )

        self.stage = StageInterface.objects.create(
            tournament = Tournament.objects.get(name = "Just A League"),
            round_num = 1
        )

        self.match = Match.objects.create(
            white_player = self.first_par,
            black_player = self.second_par,
            stage = self.stage,
            result = 1,
        )

    def test_valid_match(self):
        self._assert_valid_match()

    # Test white_player
    def test_white_player_cannot_be_blank(self):
        self.match.white_player = None
        self._assert_invalid_match()

    def test_white_player_cannot_contain_non_white_player_object(self):
        with self.assertRaises(ValueError):
            self.match.white_player = self.club

    def test_match_deletes_when_white_player_is_deleted(self):
        self.first_par.delete()
        self.assertFalse(Match.objects.filter(white_player=self.match.white_player).exists())

    def test_white_player_does_not_delete_when_match_is_deleted(self):
        self.match.delete()
        self.assertTrue(Participant.objects.filter(member = self.membership).exists())


    # Test black_player
    def test_black_player_cannot_be_blank(self):
        self.match.black_player = None
        self._assert_invalid_match()

    def test_black_player_cannot_contain_non_black_player_object(self):
        with self.assertRaises(ValueError):
            self.match.black_player = self.club

    def test_match_deletes_when_black_player_is_deleted(self):
        self.second_par.delete()
        self.assertFalse(Match.objects.filter(black_player=self.match.white_player).exists())

    def test_black_player_does_not_delete_when_match_is_deleted(self):
        self.match.delete()
        self.assertTrue(Participant.objects.filter(member = self.second_membership).exists())

    # Test stage
    def test_stage_cannot_be_blank(self):
        self.match.stage= None
        self._assert_invalid_match()

    def test_stage_cannot_contain_non_stage_object(self):
        with self.assertRaises(ValueError):
            self.match.black_player = self.club

    def test_match_deletes_when_stage_is_deleted(self):
        self.stage.delete()
        self.assertFalse(Match.objects.filter(stage=self.match.stage).exists())

    def test_stage_does_not_delete_when_match_is_deleted(self):
        self.match.delete()
        self.assertTrue(StageInterface.objects.filter(tournament = self.stage.tournament).exists())


    # Test result
    def test_result_can_be_blank(self):
        self.match.result = None
        self.match.full_clean()

    def test_result_must_not_be_other_than_options_given(self):
        self.match.result = 4
        with self.assertRaises(ValidationError):
            self.match.full_clean()

    # Constraints
    def test_white_player_and_black_plater_together_are_unique(self):
        try:
            Match.objects.create(
            white_player = self.first_par,
            black_player = self.second_par,
        )
        except(IntegrityError):
            self.assertRaises(IntegrityError)

    # Assertions
    def _assert_valid_match(self):
        try:
            self.match.full_clean()
        except (ValidationError):
            self.fail("Test Match should be valid")

    def _assert_invalid_match(self):
        with self.assertRaises(ValidationError):
            self.match.full_clean()