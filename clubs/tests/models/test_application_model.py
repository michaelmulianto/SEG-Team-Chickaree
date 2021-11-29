"""
Tests for model of a single application by some user to some club.

The model effectively represents a many-to-many relationship, however we test a single relationship.
"""

from django.test import TestCase
from clubs.models import User, Club, Application
from django.core.exceptions import ValidationError

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
            experience = 2,
            personal_statement = "I am the best applicant you can ever get."
        )

    def test_valid_app(self):
        self._assert_app_is_valid()

    # Assertions
    def _assert_app_is_valid(self):
        try:
            self.app.full_clean()
        except (ValidationError):
            self.fail("Test Application should be valid")

    def _assert_app_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.app.full_clean()

    # Test experience
    def test_exp_must_not_be_blank(self):
        self.app.experience = None
        with self.assertRaises(ValidationError):
            self.app.full_clean()

    def test_exp_must_not_be_other_than_options_given(self):
        self.app.experience = 4
        with self.assertRaises(ValidationError):
            self.app.full_clean()

    # Test personal_statement
    def test_ps_must_not_be_blank(self):
        self.app.personal_statement = None
        with self.assertRaises(ValidationError):
            self.app.full_clean()

    def test_ps_must_not_be_overlong(self):
        self.app.personal_statement = 'x' * 581
        with self.assertRaises(ValidationError):
            self.app.full_clean()
