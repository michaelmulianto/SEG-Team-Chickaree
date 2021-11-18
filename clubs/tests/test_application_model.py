from django.test import TestCase
from clubs.models import User, Club, Application
from django.core.exceptions import ValidationError

class UserModelTestCase(TestCase):
    def setUp(self):
        # called before every test
        self.user = User.objects.create_user(
            '@johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.com',
            password='Password123',
        )

        self.club = Club.objects.create(
            name = 'Club John',
            location = 'Langdon Park',
            description = 'A chess club.'
        )

        self.app = Application.objects.create(
            club = self.club,
            user = self.user
        )

    def test_valid_app(self):
        self._assert_app_is_valid()

    #assertions
    def _assert_app_is_valid(self):
        try:
            self.app.full_clean()
        except (ValidationError):
            self.fail("Test application should be valid")

    def _assert_app_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.app.full_clean()