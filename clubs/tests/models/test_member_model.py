"""
Tests for Membership model.

The table effectively represents a many-to-many relationship, however we test a single relationship.
"""

from django.test import TestCase
from clubs.models import Club, User, Membership
from django.core.exceptions import ValidationError
from django.db import IntegrityError


class MembershipModelTestCase(TestCase):
    """Test all aspects of a Membership to a club."""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    # Test setup
    def setUp(self):
        self.club = Club.objects.get(name="King\'s Knights")
        self.user = User.objects.get(username="johndoe")
        self.user_club_owner = User.objects.get(username="janedoe")
        self.membership = Membership.objects.create(
            user = self.user,
            club = self.club
        )
        self.member_club_owner = Membership.objects.create(
            user = self.user_club_owner,
            club = self.club,
            is_owner = True
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
        self.assertFalse(Membership.objects.filter(id=self.membership.id).exists())

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
        self.assertFalse(Membership.objects.filter(id=self.membership.id).exists())

    def test_user_does_not_delete_when_member_is_deleted(self):
        self.membership.delete()
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    # Test is officer field
    def test_is_officer_cannot_be_blank(self):
        self.membership.is_officer = None
        self._assert_member_is_invalid()

    def test_is_owner_must_be_boolean(self):
        self.membership.is_officer = "WRONG INPUT"
        self._assert_member_is_invalid()

    # Test is owner field
    def test_is_owner_cannot_be_blank(self):
        self.membership.is_owner = None
        self._assert_member_is_invalid()

    def test_is_owner_must_be_boolean(self):
        self.membership.is_owner = "WRONG INPUT"
        self._assert_member_is_invalid()

    # Test string
    def test_str(self):
        self.assertEqual(self.membership.__str__(), f'User: {self.user.first_name} {self.user.last_name} at Club: {self.club}')

    #Constraints:
    def test_user_and_club_together_are_unique(self):
        try:
            Membership.objects.create(
            user = self.user,
            club = self.club,
        )
        except(IntegrityError):
            self.assertRaises(IntegrityError)

    def test_club_can_only_have_one_owner_constraint(self):
        self.membership.is_owner = True
        self._assert_member_is_invalid()

    def test_member_cannot_be_owner_and_officer(self):
        with self.assertRaises(ValidationError):
            self.member_club_owner.is_officer = True
            self.member_club_owner.full_clean()

    #assertions
    def _assert_member_is_valid(self):
        try:
            self.membership.full_clean()
        except (ValidationError):
            self.fail("Test Member should be valid")

    def _assert_member_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.membership.full_clean()
