"""
Tests for Member model, found in clubs/models.py

The model effectively represents a many-to-many relationship, however we test a single relationship.
"""

from django.test import TestCase
from clubs.models import Club, User, Member
from django.core.exceptions import ValidationError


class MemberModelTestCase(TestCase):
    """Test all aspects of a Membership to a club."""

    fixtures = ['clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_user.json']

    # Test setup
    def setUp(self):
        self.club = Club.objects.get(name="King\'s Knights")
        self.user = User.objects.get(username="johndoe")
        self.membership = Member.objects.create(
            user = self.user,
            club = self.club,
        )

    def test_valid_member_object(self):
        self._assert_member_is_valid()

    # Club field tests
    def test_club_field_cannot_be_blank(self):
        self.membership.club = None
        self._assert_member_is_invalid()

    def test_club_field_cannot_contain_non_club_object(self):
        with self.assertRaises(ValueError):
            self.membership.club = self.user

    def test_member_deletes_when_club_is_deleted(self):
        self.club.delete()
        self.assertFalse(Member.objects.filter(id=self.membership.id).exists())

    def test_club_does_not_delete_when_member_is_deleted(self):
        self.membership.delete()
        self.assertTrue(Club.objects.filter(id=self.club.id).exists())

    # User field tests
    def test_user_field_cannot_be_blank(self):
        self.membership.user = None
        self._assert_member_is_invalid()

    def test_user_field_cannot_contain_non_user_object(self):
        with self.assertRaises(ValueError):
            self.membership.user = self.club

    def test_member_deletes_when_user_is_deleted(self):
        self.user.delete()
        self.assertFalse(Member.objects.filter(id=self.membership.id).exists())

    def test_user_does_not_delete_when_member_is_deleted(self):
        self.membership.delete()
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    #Constraints:
    def test_user_and_club_together_are_unique(self):
        Member.objects.create(
            user = self.user,
            club = self.club,
        )
        self._assert_member_is_invalid()

    #assertions
    def _assert_member_is_valid(self):
        try:
            self.membership.full_clean()
        except (ValidationError):
            self.fail("Test Member should be valid")

    def _assert_member_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership.full_clean()
