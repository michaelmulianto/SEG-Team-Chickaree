"""Tests for form used to create a new account"""

from django.test import TestCase
from clubs.models import User
from django import forms
from clubs.forms import SignUpForm
from django.contrib.auth.hashers import check_password

class SignUpFormTestCase(TestCase):
    """Test all aspects of the sign up forn"""

    def setUp(self):
        self.form_input = {
        'first_name': 'John',
        'last_name': 'Doe',
        'username': 'johndoe',
        'email': 'johndoe@example.com',
        'new_password': 'Password123',
        'password_confirmation': 'Password123'
        }

    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_contains_necessary_fields(self):
        form = SignUpForm()

        # Existence of fields
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)

        # Correct field for email
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

        # Check password fields are present and censor the input.
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        scd_password_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(scd_password_widget, forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'bad user'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Check validation of password format
    # Must at least have 1 upper case char, 1 lower case char and 1 number
    def test_password_must_contain_uppercase_char(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_char(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'Password'
        self.form_input['password_confirmation'] = 'Password'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_confirmation_must_be_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_saves_correctly(self):
        before_count = User.objects.count()
        form = SignUpForm(data=self.form_input)
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        user = User.objects.get(username='johndoe')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'johndoe@example.com')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
