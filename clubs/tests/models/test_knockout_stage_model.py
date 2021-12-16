"""Tests for single group model"""

from django.test import TestCase
from clubs.models import Participant, Tournament, KnockoutStage
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class KnockOutStageModelTestCase(TestCase):
    """Test all aspects of a single group model."""

    fixtures = ['clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/default_tournament.json',
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
        try:
            self.knockoutStage.get_winners()
        except(NotImplementedError):
            self.fail("get_winners() has not been implemented on knockoutStage")


    def test_get_matches_returns_the_all_the_matches_in_the_knockout_stage(self):
        self.knockoutStage.delete() #Create a knockout stage from within a tournament
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(knockout_round, KnockoutStage)
        self.assertEqual(len(knockout_round.get_matches()), 8)
        self.assertEqual(len(set(knockout_round.get_player_occurrences())), 16)

    def test_get_matches_does_not_return_matches_in_other_stages(self):
        self.knockoutStage.delete() #Create a knockout stage from within a tournament
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        first_knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(first_knockout_round, KnockoutStage)
        first_set_of_matches = first_knockout_round.get_matches()
        self.assertEqual(len(first_set_of_matches), 8)
        self.assertEqual(len(set(first_knockout_round.get_player_occurrences())), 16)

        self._complete_round_with_single_matchset(first_knockout_round)

        second_knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(second_knockout_round, KnockoutStage)
        second_set_of_matches = second_knockout_round.get_matches()
        self.assertEqual(len(second_set_of_matches), 4)
        self.assertEqual(len(set(second_knockout_round.get_player_occurrences())), 8)

        self.assertTrue(set(first_set_of_matches).isdisjoint(second_set_of_matches))

    def test_there_are_no_repeated_occurences_of_players_in_the_knockout_stage(self):
        self.knockoutStage.delete() #Create a knockout stage from within a tournament
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(knockout_round, KnockoutStage)
        first_set_of_matches = knockout_round.get_matches()
        self.assertEqual(len(first_set_of_matches), 8)
        self.assertEqual(len(set(knockout_round.get_player_occurrences())), 16)
        self.assertEqual(len(knockout_round.get_player_occurrences()), len(set(knockout_round.get_player_occurrences())))

    def test_incomplete_round_returns_false(self):
        self.knockoutStage.delete() #Create a knockout stage from within a tournament
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(knockout_round, KnockoutStage)
        first_set_of_matches = knockout_round.get_matches()
        self.assertEqual(len(first_set_of_matches), 8)
        self.assertEqual(len(set(knockout_round.get_player_occurrences())), 16)

        matches = knockout_round.get_matches()
        i = 0
        for match in matches:
            if(i != len(matches) -1): # complete all matches except one
                break
            match.result = 1
            match.save()
            i += 1

        self.assertFalse(knockout_round.get_is_complete())

    def test_complete_round_returns_true(self):
        self.knockoutStage.delete() #Create a knockout stage from within a tournament
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(knockout_round, KnockoutStage)
        first_set_of_matches = knockout_round.get_matches()
        self.assertEqual(len(first_set_of_matches), 8)
        self.assertEqual(len(set(knockout_round.get_player_occurrences())), 16)

        self._complete_round_with_single_matchset(knockout_round)

        self.assertTrue(knockout_round.get_is_complete())

    # Tests on knockout stage
    def test_get_winners_returns_all_the_winners_of_the_round(self):
        self.knockoutStage.delete() #Create a knockout stage from within a tournament
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(knockout_round, KnockoutStage)
        first_set_of_matches = knockout_round.get_matches()
        self.assertEqual(len(first_set_of_matches), 8)
        self.assertEqual(len(set(knockout_round.get_player_occurrences())), 16)

        matches = knockout_round.get_matches()
        artificial_winners = []
        for match in matches:
            match.result = 1
            match.save()
            artificial_winners.append(match.white_player)

        self.assertFalse(set(artificial_winners).isdisjoint(set(knockout_round.get_winners())))

    def test_incomplete_round_returns_none_on_get_winners(self):
        self.knockoutStage.delete() #Create a knockout stage from within a tournament
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        knockout_round = self.tournament.generate_next_round()
        self.assertIsInstance(knockout_round, KnockoutStage)
        first_set_of_matches = knockout_round.get_matches()
        self.assertEqual(len(first_set_of_matches), 8)
        self.assertEqual(len(set(knockout_round.get_player_occurrences())), 16)

        matches = knockout_round.get_matches()
        i = 0
        for match in matches:
            if(i != len(matches) -1): # complete all matches except one
                break
            match.result = 1
            match.save()
            i += 1

        self.assertEqual(knockout_round.get_winners(), None)

    # Helpers
    def _adjust_num_participants_to_capacity(self):
        participants = Participant.objects.filter(tournament=self.tournament)
        i = 0
        for p in participants:
            if i >= participants.count()-self.tournament.capacity:
                break
            p.delete()
            i += 1

    def _complete_round_with_single_matchset(self, my_round):
        matches = my_round.get_matches()
        for match in matches:
            match.result = 1 # Let white win, we don't care about specifics
            match.save()

    # Assertions
    def _assert_valid_knockout_stage(self):
        try:
            self.knockoutStage.full_clean()
        except (ValidationError):
            self.fail("Test KnockoutStage should be valid")

    def _assert_invalid_knockout_stage(self):
        with self.assertRaises(ValidationError):
            self.knockoutStage.full_clean()
