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

    #Constraints:
    def test_user_and_club_together_are_unique(self):
        try:
            Ban.objects.create(
                user = self.user,
                club = self.club,
            )
        except(IntegrityError):
            self.assertRaises(IntegrityError)

    # Test string
    def test_str(self):
        self.assertEqual(self.ban.__str__(), f'Ban: {self.user.first_name} {self.user.last_name} from Club: {self.club}')

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
