"""Tests for single group model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Match, Participant, Tournament, Club, User, Membership, GroupStage, SingleGroup,  KnockoutStage
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError


class KnockOutStageModelTestCase(TestCase):
    """Test all aspects of a single group model."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_clubs.json',
                'clubs/tests/fixtures/default_tournament.json',
                'clubs/tests/fixtures/other_tournaments.json',
                'clubs/tests/fixtures/default_tournament_participants.json'
                ]

    def setUp(self):
        
        self.tournament = Tournament.objects.get(name = 'Grand Championship' )

        self.knockoutStage = KnockoutStage.objects.create(
            tournament = self.tournament, # from TournamentStageBase which inherits RoundOfMatches
            round_num = 1, # from TournamentStageBase
        )

    def test_valid_knockout_stage(self):
        self._assert_valid_knockout_stage()

    # Tests on RoundOfMatches parent class
    def test_tournament_must_be_a_tournament_objects(self):
        try:
            self.knockoutStage.tournament = "INCORRECT INPUT"
        except(ValueError):
            pass
        else:
            self.fail("Knockout stage must be a tournament instance")

    def test_tournament_must_not_be_blank(self):
        self.knockoutStage.tournament = None
        self._assert_invalid_knockout_stage()

    def test_delete_tournament_deletes_the_knockout_stage_object(self):
        tourn_id = self.tournament.id
        self.tournament.delete()
        try:
            KnockoutStage.objects.get(tournament_id = tourn_id)
        except(ObjectDoesNotExist):
            pass
        else:
            self.fail("Knockout Stage should not exist if the tournament is deleted")
            

    def test_there_can_be_more_than_one_knockout_stage_per_tournament(self):
        new_knockoutStage = KnockoutStage.objects.create(
            tournament = self.tournament
        )
        try:
            new_knockoutStage.full_clean()
        except(ValidationError):
            self.fail("A tournament must be able to have more than one knockout stage")


    # Tests on TournameStageBase parent class
    def test_round_num_has_a_default_value_of_1(self):
        new_knockoutStage = KnockoutStage.objects.create(
            tournament = self.tournament
        )
        self.assertEqual(new_knockoutStage.round_num, 1)

    def test_round_num_cannot_be_blank(self):
        self.knockoutStage.round_num = None
        self._assert_invalid_knockout_stage()

    def test_round_num_has_to_be_an_int(self):
        self.knockoutStage.round_num = "INCORRECT INPUT"
        self._assert_invalid_knockout_stage()

    def test_get_stage_gives_us_a_knockout_stage(self):
        stage = self.knockoutStage.get_stage()
        self.assertTrue(isinstance(stage, KnockoutStage))
    
    # Tests on StageMethodInterface parent class
    def test_get_winners_does_return_NotImplementedError(self):
        pass

    def test_get_matches_returns_the_all_the_matches_in_the_knockout_stage(self):
        pass

    def test_get_matches_does_not_return_matches_in_other_stages(self):
        pass

    def test_get_player_occurences_returns_all_the_player_occurences_in_the_knockout_stage(self):
        pass

    def test_there_are_no_repeated_occurences_of_players_in_the_knockout_stage(self):
        pass

    def test_incomplete_round_returns_false(self):
        pass

    def test_complete_round_returns_true(self):
        pass

    # Tests on knockout stage
    def test_get_winners_returns_all_the_winners_of_the_round(self):
        pass

    def test_incomplete_round_returns_none_on_get_winners(self):
        pass


    # Assertions
    def _assert_valid_knockout_stage(self):
        try:
            self.knockoutStage.full_clean()
        except (ValidationError):
            self.fail("Test KnockoutStage should be valid")

    def _assert_invalid_knockout_stage(self):
        with self.assertRaises(ValidationError):
            self.knockoutStage.full_clean()
