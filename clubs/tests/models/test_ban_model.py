"""
Tests for model of a single ban for some user to some club.

The model effectively represents a many-to-many relationship, however we test a single relationship.
"""

from django.db.utils import IntegrityError
from django.test import TestCase
from clubs.models import User, Club, Ban
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class BanModelTestCase(TestCase):
    """Test all attributes included in the ban model"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        # called before every test
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name="King\'s Knights")
        self.ban = Ban.objects.create(
            club = self.club,
            user = self.user,
        )

    def test_valid_ban(self):
        self._assert_ban_is_valid()

    # Test club
    def test_club_field_cannot_be_blank(self):
        self.ban.club = None
        self._assert_ban_is_invalid()

    def test_club_field_cannot_contain_non_club_object(self):
        with self.assertRaises(ValueError):
            self.ban.club = self.user

    def test_ban_deletes_when_club_is_deleted(self):
        self.club.delete()
        self.assertFalse(Ban.objects.filter(id=self.ban.id).exists())

    def test_club_does_not_delete_when_ban_is_deleted(self):
        self.ban.delete()
        self.assertTrue(Club.objects.filter(id=self.club.id).exists())

    # Test user
    def test_user_field_cannot_be_blank(self):
        self.ban.user = None
        self._assert_ban_is_invalid()

    def test_user_field_cannot_contain_non_user_object(self):
        with self.assertRaises(ValueError):
            self.ban.user = self.club

    def test_ban_deletes_when_user_is_deleted(self):
        self.user.delete()
        self.assertFalse(Ban.objects.filter(id=self.ban.id).exists())

    def test_user_does_not_delete_when_ban_is_deleted(self):
        self.ban.delete()
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    #Constraints:
    def test_user_and_club_together_are_unique(self):
        try:
            Ban.objects.create(
                user = self.user,
                club = self.club,
            )
        except(IntegrityError):
            self.assertRaises(IntegrityError)



    # Assertions
    def _assert_ban_is_valid(self):
        try:
            self.ban.full_clean()
        except (ValidationError):
            self.fail("Test Ban should be valid")

    def _assert_ban_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.ban.full_clean()

    def _assert_ban_is_invlid_do_to_integrity_constraint(self):
        with self.assertRaises(IntegrityError):
            self.ban.full_clean()
