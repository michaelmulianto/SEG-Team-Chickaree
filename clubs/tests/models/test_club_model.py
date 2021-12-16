"""Tests for Club model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Club, Membership, User, Ban, Application
from django.core.exceptions import ValidationError


class ClubModelTestCase(TestCase):
    """Test all aspects of a club."""

    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/other_clubs.json', 'clubs/tests/fixtures/default_user.json']

    # Test setup
    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.club = Club.objects.get(name="King\'s Knights")
        self.second_club = Club.objects.get(name="Queen\'s Rooks")

    def test_valid_message(self):
        self._assert_club_is_valid()

    # Test name
    def test_name_must_not_be_blank(self):
        self.club.name = None
        self._assert_club_is_invalid()

    def test_name_must_be_unique(self):
        self.club.name = self.second_club.name
        self._assert_club_is_invalid()

    def test_name_must_not_be_over_50_characters(self):
        self.club.name = 'x' * 51
        self._assert_club_is_invalid()

    def test_name_can_be_50_characters(self):
        self.club.name = 'x' * 50
        self._assert_club_is_valid()

    # Test location
    def test_location_must_not_be_blank(self):
        self.club.location = None
        self._assert_club_is_invalid()

    def test_location_is_not_unique(self):
        self.club.location = self.second_club.location
        self._assert_club_is_valid()

    def test_location_must_not_be_over_50_characters(self):
        self.club.location = 'x' * 51
        self._assert_club_is_invalid()

    def test_location_can_be_50_characters(self):
        self.club.location = 'x' * 50
        self._assert_club_is_valid()

    # Test description
    def test_description_must_not_be_blank(self):
        self.club.description = None
        self._assert_club_is_invalid()

    def test_description_must_not_be_over_280_characters(self):
        self.club.description = 'x' * 281
        self._assert_club_is_invalid()

    def test_description_can_be_280_characters(self):
        self.club.description = 'x' * 280
        self._assert_club_is_valid()

    def test_description_is_not_unique(self):
        self.club.description = self.second_club.description
        self._assert_club_is_valid()

    # Test string
    def test_str(self):
        self.assertEqual(self.club.__str__(), self.club.name)

    # Test get get memberships
    def test_get_memberships(self):
        self.assertEqual(len(self.club.get_memberships()), 0)
        self.member = Membership.objects.create(
            user = self.user,
            club = self.club,
        )
        self.assertEqual(len(self.club.get_memberships()), 1)

    # Test get banned members
    def test_get_banned_members(self):
        self.assertEqual(len(self.club.get_memberships()), 0)
        self.ban = Ban.objects.create(
            club = self.club,
            user = self.user,
        )
        self.assertEqual(len(self.club.get_banned_members()), 1)

    # Test get applications
    def test_get_applications(self):
        self.app = Application.objects.create(
            club = self.club,
            user = self.user,
            personal_statement = "I am the best applicant you can ever get."
        )
        self.assertEqual(len(self.club.get_applications()), 1)

    # Test get Officers
    def test_get_officers(self):
        self.member = Membership.objects.create(
            user = self.user,
            club = self.club,
            is_officer = True
        )
        self.assertEqual(len(self.club.get_officers()), 1)

    #Test get Owner
    def test_get_officers(self):
        self.member = Membership.objects.create(
            user = self.user,
            club = self.club,
            is_owner = True
        )
        self.assertEqual(self.club.get_owner(), self.member)

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
