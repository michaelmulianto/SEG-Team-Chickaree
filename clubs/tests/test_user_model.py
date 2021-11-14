"""Tests for User model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import User
from django.core.exceptions import ValidationError

class UserModelTestCase(TestCase):
    """Test all aspects of a user."""

    # Test setup
    def setUp(self):
        self.user = User.objects.create_user(
            'johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.com',
            password='Password123',
        )

    def test_valid_user(self):
        self._assert_user_is_valid()

    # Test username
    def test_username_cannot_be_blank(self):
        self.user.username =''
        self._assert_user_is_invalid()

    def test_username_can_be_32_chars_long(self):
        self.user.username = 'x' * 32
        self._assert_user_is_valid()

    def test_username_cannot_be_33_chars_long(self):
        self.user.username = 'x' * 33
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        User.objects.create_user(
            'janedoe',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.com',
            password='Password123',
        )
        self.user.username = 'janedoe'
        self._assert_user_is_invalid()

    def test_username_must_contain_only_alphanumbericals(self):
        self.user.username = '@john!doe'
        self._assert_user_is_invalid()

    def test_username_must_be_min_3_long(self):
        self.user.username = 'hi'
        self._assert_user_is_invalid()

    def test_username_may_contain_numbers(self):
        self.user.username = 'j0hndoe2'
        self._assert_user_is_valid()

    # Test first_name
    def test_first_name_cannot_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_can_already_exist(self):
        User.objects.create_user(
            'janedoe',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.com',
            password='Password123',
        )
        self.user.first_name = 'Jane'
        self._assert_user_is_valid()

    def test_first_name_can_be_48_long(self):
        self.user.first_name = 'j' * 48
        self._assert_user_is_valid()

    def test_first_name_cannot_be_49_long(self):
        self.user.first_name = 'j' * 49
        self._assert_user_is_invalid()

    def test_first_name_must_contain_only_letters(self):
        self.user.first_name = 'J0hn'
        self._assert_user_is_invalid()

    # Test last_name
    def test_last_name_cannot_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_can_already_exist(self):
        User.objects.create_user(
            'janedoe',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.com',
            password='Password123',
        )
        self.user.last_name = 'Doe'
        self._assert_user_is_valid()

    def test_last_name_can_be_48_long(self):
        self.user.last_name = 'j' * 48
        self._assert_user_is_valid()

    def test_last_name_cannot_be_49_long(self):
        self.user.last_name = 'j' * 49
        self._assert_user_is_invalid()

    def test_last_name_must_contain_only_letters(self):
        self.user.last_name = 'D0e'
        self._assert_user_is_invalid()

    # Test email
    def test_email_must_be_unique(self):
        User.objects.create_user(
            'janedoe',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.com',
            password='Password123',
        )
        self.user.email= 'janedoe@example.com'
        self._assert_user_is_invalid()

    def test_email_cannot_have_no_at_symbol(self):
        self.user.email = 'johndoeexample.com'
        self._assert_user_is_invalid()

    def test_email_cannot_have_2_at_symbols(self):
        self.user.email = 'johndoe@@example.com'
        self._assert_user_is_invalid()

    def test_email_cannot_have_no_dots_after_at(self):
        self.user.email = 'johndoe@examplecom'
        self._assert_user_is_invalid()

    def test_email_can_have_special_characters_before_at(self):
        self.user.email = 'john.doe!+@example.com'
        self._assert_user_is_valid()

    def test_email_cannot_have_special_characters_after_at(self):
        self.user.email = 'johndoe@example!.com'
        self._assert_user_is_invalid()

    # Helper functions.
    # Generic assertions.
    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail("Test user should be valid")

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
