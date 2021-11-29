"""Tests for Club model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Club
from django.core.exceptions import ValidationError


class ClubModelTestCase(TestCase):
    """Test all aspects of a club."""

    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/second_club.json']

    # Test setup
    def setUp(self):
        self.club = Club.objects.get(name="King\'s Knights")
        self.second_club = Club.objects.get(name="Queen\'s Rooks")

    def test_valid_message(self):
        try:
            self.club.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    # Test name
    def test_name_must_not_be_blank(self):
        self.club.name = None
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_name_must_be_unique(self):
        self.club.name = self.second_club.name
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_name_must_not_be_over_50_characters(self):
        self.club.name = 'x' * 51
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    # Test location
    def test_location_must_not_be_blank(self):
        self.club.location = None
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_location_is_not_unique(self):
        self.club.location = self.second_club.location
        self._assert_club_is_valid()

    def test_location_must_not_be_over_50_characters(self):
        self.club.location = 'x' * 51
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    # Test description
    def test_description_must_not_be_blank(self):
        self.club.description = None
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_description_must_not_be_over_280_characters(self):
        self.club.description = 'x' * 281
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_description_is_not_unique(self):
        self.club.description = self.second_club.description
        self._assert_club_is_valid()

    # Helper functions.
    # Generic assertions.
    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail("Test club should be valid")

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()