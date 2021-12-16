"""Tests for User model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import User, Membership, Club
from django.core.exceptions import ValidationError

class UserModelTestCase(TestCase):
    """Test all aspects of a user."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    # Test setup
    def setUp(self):
        self.user = User.objects.get(username='johndoe')

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
        self.user.email= 'janedoe@example.org'
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

    #Test bio
    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_may_not_be_unique(self):
        self.user.bio = 'Jane here. I like chess.'
        self._assert_user_is_valid()

    def test_bio_may_be_520_characters_long(self):
        self.user.bio = 'x' * 520
        self._assert_user_is_valid()

    def test_bio_must_not_be_over_520_characters_long(self):
        self.user.bio = 'x' * 521
        self._assert_user_is_invalid()

    # Test experience
    def test_exp_must_not_be_blank(self):
        self.user.experience = None
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_exp_must_not_be_other_than_options_given(self):
        self.user.experience = 4
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    #Test gravatar
    def test_default_gravatar(self):
        expected = "https://www.gravatar.com/avatar/363c1b0cd64dadffb867236a00e62986?size=120&default=mp"
        self.assertEqual(self.user.gravatar(), expected)

    def test_gravatar_custom_size(self):
        size = 500
        expected = "https://www.gravatar.com/avatar/363c1b0cd64dadffb867236a00e62986?size=" + str(size) + "&default=mp"
        self.assertEqual(self.user.gravatar(size), expected)

    def test_mini_gravatar(self):
        expected = "https://www.gravatar.com/avatar/363c1b0cd64dadffb867236a00e62986?size=50&default=mp"
        self.assertEqual(self.user.mini_gravatar(), expected)

    # Test get clubs
    def test_get_clubs(self):
        self.club = Club.objects.get(name="King\'s Knights")
        Membership.objects.create(
            user = self.user,
            club = self.club,
        )
        self.assertEqual(len(self.user.get_clubs()), 1)

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
