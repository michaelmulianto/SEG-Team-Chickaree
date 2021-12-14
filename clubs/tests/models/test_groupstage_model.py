"""Tests for model of a group stage."""

from django.test import TestCase
from clubs.models import Participant, Tournament, GroupStage, SingleGroup
from django.core.exceptions import ValidationError

class GroupStageModelTestCase(TestCase):
    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_tournament.json',
    'clubs/tests/fixtures/default_tournament_participants.json'
    ]

    def setUp(self):
        self.tournament = Tournament.objects.get(id=1)
        self.group_stage = self.tournament.generate_next_round()

    def test_valid_group_stage(self):
        # Ensure the fixtures are correct
        self.assertEqual(self.tournament.capacity, 96)
        self.assertEqual(self.tournament.capacity, Participant.objects.filter(tournament=self.tournament).count())

        self._assert_valid_groupstage()

    def test_groups_must_be_assigned_to_group_stage(self):
        SingleGroup.objects.filter(group_stage=self.group_stage).delete()
        self._assert_invalid_groupstage()

    def test_correct_number_of_matches_are_returned_for_96_man_round(self):
        self.assertEqual(len(self.group_stage.get_matches()), 240)

    def test_get_is_complete_and_get_winners_on_unfinished_round(self):
        self.assertFalse(self.group_stage.get_is_complete())
        self.assertEqual(self.group_stage.get_winners(), None)

    def test_get_is_complete_and_get_winners_on_finished_round(self):
        expected_winners = []
        for match in self.group_stage.get_matches():
            match.result = 1
            match.save()

        for group in SingleGroup.objects.filter(group_stage = self.group_stage):
            expected_winners += group.get_winners()

        self.assertTrue(self.group_stage.get_is_complete())
        actual_winners = self.group_stage.get_winners()
        self.assertEqual(set(actual_winners), set(expected_winners))
        self.assertEqual(len(actual_winners), len(set(actual_winners)))

    def test_get_player_occurences_returns_size_of_group_minus_one_per_player(self):
        test_participant = Participant.objects.filter(tournament=self.tournament)[0]
        count = 0
        for occurrence in self.group_stage.get_player_occurrences():
            if occurrence == test_participant:
                count+=1

        self.assertEqual(count, 5)

    # Assertions
    def _assert_valid_groupstage(self):
        try:
            self.group_stage.full_clean()
        except (ValidationError):
            self.fail("Test group stage should be valid")

    def _assert_invalid_groupstage(self):
        with self.assertRaises(ValidationError):
            self.group_stage.full_clean()