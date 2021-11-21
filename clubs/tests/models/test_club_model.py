"""Tests for Club model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Club
from django.core.exceptions import ValidationError


class ClubModelTestCase(TestCase):
    """Test all aspects of a club."""

    # Test setup
    def setUp(self):
        self.club = Club(
            name = 'Knight',
            location = 'London',
            description = 'This is the best London chess club yet.',
        )

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

    def test_name_must_not_be_overlong(self):
        self.club.name = 'x' * 51
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    # Test location
    def test_location_must_not_be_blank(self):
        self.club.location = None
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_location_must_not_be_overlong(self):
        self.club.location = 'x' * 51
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    # Test description
    def test_description_must_not_be_blank(self):
        self.club.description = None
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_description_must_not_be_overlong(self):
        self.club.description = 'x' * 281
        with self.assertRaises(ValidationError):
            self.club.full_clean()
