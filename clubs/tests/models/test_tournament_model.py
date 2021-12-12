"""Tests for Tournament model, found in tournaments/models.py"""

from django.test import TestCase
from clubs.models import Tournament, Membership, User, Participant, GroupStage, KnockoutStage, SingleGroup, Match, StageInterface
from django.core.exceptions import ValidationError


class TournamentModelTestCase(TestCase):
    """Test all aspects of a tournament."""

    fixtures = ['clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_tournament.json',
        'clubs/tests/fixtures/other_tournaments.json', 
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_tournament_participants.json'
        ]

    # Test setup
    def setUp(self):
        self.tournament = Tournament.objects.get(name="Grand Championship")
        self.second_tournament = Tournament.objects.get(name="Just A League")
        self.dummy_member = Membership.objects.create(
            user = User.objects.get(username='janedoe'),
            club = self.tournament.club
        )

    def test_valid_tournament(self):
        self._assert_tournament_is_valid()

    # Test name
    def test_name_must_not_be_blank(self):
        self.tournament.name = None
        self._assert_tournament_is_invalid()

    def test_name_must_be_unique(self):
        self.tournament.name = self.second_tournament.name
        self._assert_tournament_is_invalid()

    def test_name_must_not_be_over_50_characters(self):
        self.tournament.name = 'x' * 51
        self._assert_tournament_is_invalid()

    def test_name_can_be_50_characters(self):
        self.tournament.name = 'x' * 50
        self._assert_tournament_is_valid()

    # Test capacity
    def test_capacity_must_not_be_blank(self):
        self.tournament.capacity = None
        Participant.objects.filter(tournament=self.tournament).delete()
        self._assert_tournament_is_invalid()

    def test_capacity_is_not_unique(self):
        self.tournament.capacity = self.second_tournament.capacity
        self._adjust_num_participants_to_capacity()
        self._assert_tournament_is_valid()

    def test_capacity_is_positive(self):
        self.tournament.capacity = -1
        Participant.objects.filter(tournament=self.tournament).delete()
        self._assert_tournament_is_invalid()

    def test_capacity_must_be_divisible_by_4_when_above_16(self):
        self.tournament.capacity = 18 # Divisible by 6
        self._adjust_num_participants_to_capacity()
        self._assert_tournament_is_invalid()

    def test_capacity_must_be_divisible_by_6_when_above_16(self):
        self.tournament.capacity = 28 # Divisible by 4
        self._adjust_num_participants_to_capacity()
        self._assert_tournament_is_invalid()

    def test_capacity_can_be_32(self):
        self.tournament.capacity = 32
        self._adjust_num_participants_to_capacity()
        self._assert_tournament_is_valid()

    def test_capacity_must_be_divisble_by_8_above_32(self):
        self.tournament.capacity = 36 # Divisible by 4 and 6
        self._adjust_num_participants_to_capacity()
        self._assert_tournament_is_invalid()

    def test_capacity_is_greater_than_1(self):
        self.tournament.capacity = 1
        self._adjust_num_participants_to_capacity()
        self._assert_tournament_is_invalid()

    def test_capacity_is_less_than_97(self):
        self.tournament.capacity = 97
        self._assert_tournament_is_invalid()

    # Test description
    def test_description_must_not_be_blank(self):
        self.tournament.description = None
        self._assert_tournament_is_invalid()

    def test_description_must_not_be_over_280_characters(self):
        self.tournament.description = 'x' * 281
        self._assert_tournament_is_invalid()

    def test_description_can_be_280_characters(self):
        self.tournament.description = 'x' * 280
        self._assert_tournament_is_valid()

    def test_description_is_not_unique(self):
        self.tournament.description = self.second_tournament.description
        self._assert_tournament_is_valid()

    # Test deadline date time
    def test_deadline_must_not_be_blank(self):
        self.tournament.deadline = None
        self._assert_tournament_is_invalid()

    def test_deadline_must_be_before_the_start_date(self):
        self.tournament.deadline = "2021-12-20T00:00:00+00:00"
        self.tournament.start = "2021-12-19T00:00:00+00:00"
        self._assert_tournament_is_invalid()

    # Test start date time
    def test_start_must_not_be_blank(self):
        self.tournament.start = None
        self._assert_tournament_is_invalid()

    # Test end date time
    def test_end_must_not_be_blank(self):
        self.tournament.end = None
        self._assert_tournament_is_invalid()

    def test_end_must_not_be_before_the_start_date(self):
        self.tournament.start = "2021-12-02T00:00:00+00:00"
        self.tournament.end = "2021-12-01T00:00:00+00:00"
        self._assert_tournament_is_invalid()

    # Test participant constraints
    def test_more_participants_than_capacity(self):
        Participant.objects.create(
            tournament=self.tournament,
            member=self.dummy_member
        )
        self._assert_tournament_is_invalid()

    # Test num participants

    def test_num_participants(self):
        self.assertEqual(self.tournament.get_num_participants(), self.tournament.capacity)

    # Test get max round num
    def test_max_round_num_over_32_participants(self):
        self.assertEqual(self.tournament.get_max_round_num(), 6)
    
    def test_max_round_num_over_16_under_33_participants(self):
        self.tournament.capacity = 32
        self._adjust_num_participants_to_capacity()
        self.assertEqual(self.tournament.get_max_round_num(), 5)

    def test_max_round_num_16_participants(self):
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        self.assertEqual(self.tournament.get_max_round_num(), 4)

    def test_max_round_num_8_participants(self):
        self.tournament.capacity = 8
        self._adjust_num_participants_to_capacity()
        self.assertEqual(self.tournament.get_max_round_num(), 3)

    def test_max_round_num_4_participants(self):
        self.tournament.capacity = 4
        self._adjust_num_participants_to_capacity()
        self.assertEqual(self.tournament.get_max_round_num(), 2)

    def test_max_round_num_2_participants(self):
        self.tournament.capacity = 2
        self._adjust_num_participants_to_capacity()
        self.assertEqual(self.tournament.get_max_round_num(), 1)

    def test_max_round_num_0_participants(self):
        self.tournament.capacity = 0
        self._adjust_num_participants_to_capacity()
        self.assertEqual(self.tournament.get_max_round_num(), 0)
    
    # Test generate initial round
    def test_None_returned_when_generating_next_round_with_no_participants(self):
        Participant.objects.filter(tournament=self.tournament).delete()
        self.assertEqual(self.tournament.generate_next_round(), None)

    def test_generate_first_round_with_32_participants(self):
        self.tournament.capacity = 32
        self._adjust_num_participants_to_capacity()
        next_round = self.tournament.generate_next_round()
        self.assertIsInstance(next_round, GroupStage)
        groups = SingleGroup.objects.filter(group_stage=next_round)
        self.assertEqual(groups.count(), 8)
        groups[0].full_clean()
        # Check num members in one group
        self.assertEqual(len(set(groups[0].get_player_occurences())), 4)
        # Check number of matches in one group
        self.assertEqual(len(groups[0].get_matches()), 6)
    
    def test_generate_first_round_with_48_participants(self):
        self.tournament.capacity = 48
        self._adjust_num_participants_to_capacity()
        next_round = self.tournament.generate_next_round()
        self.assertIsInstance(next_round, GroupStage)
        groups = SingleGroup.objects.filter(group_stage=next_round)
        self.assertEqual(groups.count(), 8)
        groups[0].full_clean()
        # Check num members in one group
        self.assertEqual(len(set(groups[0].get_player_occurences())), 6)
        # Check number of matches in one group
        self.assertEqual(len(groups[0].get_matches()), 15)

    def test_generate_first_round_with_96_participants(self):
        # 96 participants by default in fixture
        next_round = self.tournament.generate_next_round()
        self.assertIsInstance(next_round, GroupStage)
        groups = SingleGroup.objects.filter(group_stage=next_round)
        self.assertEqual(groups.count(), 16)
        groups[0].full_clean()
        # Check num members in one group
        self.assertEqual(len(set(groups[0].get_player_occurences())), 6)
        # Check number of matches in one group
        self.assertEqual(len(groups[0].get_matches()), 15)

    def test_generate_first_round_with_16_participants(self):
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        next_round = self.tournament.generate_next_round()
        self.assertIsInstance(next_round, KnockoutStage)
        # Check num members in round
        self.assertEqual(len(set(next_round.get_player_occurences())), 16)
        # Check correct number of matches played
        self.assertEqual(len(next_round.get_matches()), 8)

    def test_generate_first_round_with_invalid_number_of_participants(self):
        with self.assertRaises(ValidationError):
            self.tournament.capacity = 47
            self._adjust_num_participants_to_capacity()
            next_round = self.tournament.generate_next_round()

    # Test generate subsequent rounds

    def test_round_after_6_player_group_stage_is_4_player_group_stage_with_32_participants(self):
        # First we must play initial round...
        # 96 Participants = 6 player group, tested above
        first_round = self.tournament.generate_next_round()
        self.assertIsInstance(first_round, GroupStage)
        self._complete_group_round(first_round)

        next_round = self.tournament.generate_next_round()
        self.assertIsInstance(next_round, GroupStage)
        groups = SingleGroup.objects.filter(group_stage=next_round)
        self.assertEqual(groups.count(), 8)
        # Check num members in one group, as 8*4=32
        self.assertEqual(len(set(groups[0].get_player_occurences())), 4)

    def test_round_after_4_player_group_stage_is_knockout_with_16_players(self):
        self.tournament.capacity = 32
        self._adjust_num_participants_to_capacity()
        first_round = self.tournament.generate_next_round()
        self.assertIsInstance(first_round, GroupStage)
        self._complete_group_round(first_round)

        next_round = self.tournament.generate_next_round()
        self.assertIsInstance(next_round, KnockoutStage)
        self.assertEqual(len(next_round.get_matches()), 8)
        self.assertEqual(len(set(next_round.get_player_occurences())), 16)

    def test_round_after_knockout_is_knockout(self):
        self.tournament.capacity = 16
        self._adjust_num_participants_to_capacity()
        first_round = self.tournament.generate_next_round()
        self.assertIsInstance(first_round, KnockoutStage)
        self._complete_round_with_single_matchset(first_round)

        next_round = self.tournament.generate_next_round()
        self.assertIsInstance(next_round, KnockoutStage)
        self.assertEqual(len(next_round.get_matches()), 4)
        self.assertEqual(len(set(next_round.get_player_occurences())), 8)

    def test_round_after_2_player_knockout_is_None(self):
        self.tournament.capacity = 2
        self._adjust_num_participants_to_capacity()
        first_round = self.tournament.generate_next_round()
        self.assertIsInstance(first_round, KnockoutStage)
        self._complete_round_with_single_matchset(first_round)

        next_round = self.tournament.generate_next_round()
        self.assertEqual(next_round, None)

    # Helper functions.
    def _adjust_num_participants_to_capacity(self):
        participants = Participant.objects.filter(tournament=self.tournament)
        i = 0
        for p in participants:
            if i >= participants.count()-self.tournament.capacity:
                break
            p.delete()
            i += 1

    def _complete_group_round(self, my_round):
        groups = SingleGroup.objects.filter(group_stage=my_round)
        for group in groups:
            self._complete_round_with_single_matchset(group)

    def _complete_round_with_single_matchset(self, my_round):
        matches = my_round.get_matches()
        for match in matches:
            match.result = 1 # Let white win, we don't care about specifics
            match.save()

    # Generic assertions.
    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except (ValidationError):
            self.fail("Test tournament should be valid")

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
