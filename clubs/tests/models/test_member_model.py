"""Tests for Member model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Club, User, Member
from django.core.exceptions import ValidationError


class MemberModelTestCase(TestCase):
    """Test all aspects of a club."""

    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_club.json']

    # Test setup
    def setUp(self):
        self.club = Club.objects.get(name="King\'s Knights")
        self.user = User.objects.get(username="johndoe")
        self.membership = Member.objects.create(
            user = self.user
            club = self.club
        )

    def test_valid_member_object(self):
        self._assert_member_is_valid()

    def test_club_field_cannot_be_blank(self):
        self._assert_member_is_valid()

    #assertions
    def _assert_member_is_valid(self):
        try:
            self.membership.full_clean()
        except (ValidationError):
            self.fail("Test Application should be valid")

    def _assert_member_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership.full_clean()