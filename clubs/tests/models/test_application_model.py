"""
Tests for model of a single application by some user to some club.

The model effectively represents a many-to-many relationship, however we test a single relationship.
"""

from django.db.utils import IntegrityError
from django.test import TestCase
from clubs.models import User, Club, Application
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class ApplicationModelTestCase(TestCase):
    """Test all attributes included in the application model"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        # called before every test
        self.user = User.objects.get(username='johndoe')

        self.club = Club.objects.get(name="King\'s Knights")

        self.app = Application.objects.create(
            club = self.club,
            user = self.user,
            personal_statement = "I am the best applicant you can ever get."
        )

    def test_valid_app(self):
        self._assert_app_is_valid()

    # Test club
    def test_club_field_cannot_be_blank(self):
        self.app.club = None
        self._assert_app_is_invalid()

    def test_club_field_cannot_contain_non_club_object(self):
        with self.assertRaises(ValueError):
            self.app.club = self.user

    def test_application_deletes_when_club_is_deleted(self):
        self.club.delete()
        self.assertFalse(Application.objects.filter(id=self.app.id).exists())

    def test_club_does_not_delete_when_application_is_deleted(self):
        self.app.delete()
        self.assertTrue(Club.objects.filter(id=self.club.id).exists())

    # Test user
    def test_user_field_cannot_be_blank(self):
        self.app.user = None
        self._assert_app_is_invalid()

    def test_user_field_cannot_contain_non_user_object(self):
        with self.assertRaises(ValueError):
            self.app.user = self.club

    def test_member_deletes_when_user_is_deleted(self):
        self.user.delete()
        self.assertFalse(Application.objects.filter(id=self.app.id).exists())

    def test_user_does_not_delete_when_member_is_deleted(self):
        self.app.delete()
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    # Test personal_statement
    def test_ps_must_not_be_blank(self):
        self.app.personal_statement = None
        with self.assertRaises(ValidationError):
            self.app.full_clean()

    def test_ps_must_not_be_overlong(self):
        self.app.personal_statement = 'x' * 581
        with self.assertRaises(ValidationError):
            self.app.full_clean()

    #Constraints:
    def test_user_and_club_together_are_unique(self):
        try:
            Application.objects.create(
                user = self.user,
                club = self.club,
            )
        except(IntegrityError):
            self.assertRaises(IntegrityError)

    # Assertions
    def _assert_app_is_valid(self):
        try:
            self.app.full_clean()
        except (ValidationError):
            self.fail("Test Application should be valid")

    def _assert_app_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.app.full_clean()
