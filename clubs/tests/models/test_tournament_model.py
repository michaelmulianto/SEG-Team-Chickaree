"""Tests for Tournament model, found in tournaments/models.py"""

from django.test import TestCase
from clubs.models import Tournament
from django.core.exceptions import ValidationError


class TournamentModelTestCase(TestCase):
    """Test all aspects of a tournament."""

    fixtures = ['clubs/tests/fixtures/default_club.json','clubs/tests/fixtures/default_tournament.json',
        'clubs/tests/fixtures/other_tournaments.json'
        ]

    # Test setup
    def setUp(self):
        self.tournament = Tournament.objects.get(name="Grand Championship")
        self.second_tournament = Tournament.objects.get(name="Just A League")

    def test_valid_message(self):
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
        self._assert_tournament_is_invalid()

    def test_capacity_is_not_unique(self):
        self.tournament.capacity = self.second_tournament.capacity
        self._assert_tournament_is_valid()

    def test_capacity_is_positive(self):
        self.tournament.capacity = -1
        self._assert_tournament_is_invalid()

    def test_capacity_must_be_divisible_by_4_when_above_16(self):
        self.tournament.capacity = 18 # Divisible by 6
        self._assert_tournament_is_invalid()

    def test_capacity_must_be_divisible_by_6_when_above_16(self):
        self.tournament.capacity = 28 # Divisible by 4
        self._assert_tournament_is_invalid()

    def test_capacity_can_be_32(self):
        self.tournament.capacity = 32
        self._assert_tournament_is_invalid()

    def test_capacity_must_be_divisble_by_8_above_32(self):
        self.tournament.capacity = 36 # Divisible by 4 and 6
        self._assert_tournament_is_invalid()

    def test_capacity_is_greater_than_1(self):
        self.tournament.capacity = 1
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

    # Test start date time
    def test_start_must_not_be_blank(self):
        self.tournament.start = None
        self._assert_tournament_is_invalid()

    def test_start_must_not_be_in_the_past(self):
        self.tournament.start= "2021-12-01T00:00:00+00:00"
        self._assert_tournament_is_invalid()

    # Test start date time
    def test_end_must_not_be_blank(self):
        self.tournament.end = None
        self._assert_tournament_is_invalid()

    def test_end_must_not_be_in_the_past(self):
        self.tournament.start = "2021-12-02T00:00:00+00:00"
        self._assert_tournament_is_invalid()

    def test_end_must_not_be_before_the_start_date(self):
        self.tournament.start = "2021-12-02T00:00:00+00:00"
        self.tournament.end = "2021-12-01T00:00:00+00:00"
        self._assert_tournament_is_invalid()

    # Helper functions.
    # Generic assertions.
    def _assert_tournament_is_valid(self):
        try:
            self.tournament.full_clean()
        except (ValidationError):
            self.fail("Test tournament should be valid")

    def _assert_tournament_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.tournament.full_clean()
