"""
Test backend implementation of password changing.

Note: a built in password change form is being used, hence the lack of tests specific to the front end.
"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from clubs.tests.helpers import LogInTester

class ChangePasswordViewTestCase(TestCase, LogInTester):
    """Test all aspects of change password view."""
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.url = reverse('change_password')

    def test_change_password_url(self):
        self.assertEqual(self.url, '/change_password/')

    def test_get_change_password_form(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'change_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangeForm))
        self.assertFalse(form.is_bound)

    def test_successful_password_change(self):
        pass