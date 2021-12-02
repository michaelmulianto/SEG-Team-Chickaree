"""
Test backend implementation of password changing.

Note: a built in password change form is being used, hence the lack of tests specific to the front end.
"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin

class ChangePasswordViewTestCase(TestCase, MenuTesterMixin):
    """Test all aspects of change password view."""
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
        self.data = {
            'old_password': 'Password123',
            'new_password1': 'NewPass12',
            'new_password2': 'NewPass12',
        }
        self.url = reverse('change_password')

    def test_change_password_url(self):
        self.assertEqual(self.url, '/change_password/')

    def test_get_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_change_password_form(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)
        self.assert_menu(response)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'change_password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangeForm))
        self.assertFalse(form.is_bound)

    def test_successful_password_change(self):
        self.client.login(username="johndoe", password="Password123")
        old_pass = self.user.password
        response = self.client.post(self.url, self.data, follow=True)
        self.user = self._get_updated_self_user()
        new_pass = self.user.password
        self.assertNotEqual(old_pass,new_pass)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'account.html')

    # Test invalid inputs
    def test_password_validation_used(self):
        self.data['new_password1'] = 'badpass'
        self.data['new_password2'] = 'badpass'
        self.client.login(username="johndoe", password="Password123")
        old_pass = self.user.password
        response = self.client.post(self.url, self.data, follow=True)
        self.user = self._get_updated_self_user()
        new_pass = self.user.password
        self.assertEqual(old_pass,new_pass)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'change_password.html')

    def test_password_confirmation_must_equal_new_password(self):
        self.data['new_password2'] = 'NotSame1'
        self.client.login(username="johndoe", password="Password123")
        old_pass = self.user.password
        response = self.client.post(self.url, self.data, follow=True)
        self.user = self._get_updated_self_user()
        new_pass = self.user.password
        self.assertEqual(old_pass,new_pass)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'change_password.html')

    def test_password_change_fails_when_old_password_is_wrong(self):
        self.data['old_password'] = 'Fail!'
        self.client.login(username="johndoe", password="Password123")
        old_pass = self.user.password
        response = self.client.post(self.url, self.data, follow=True)
        self.user = self._get_updated_self_user()
        new_pass = self.user.password
        self.assertEqual(old_pass,new_pass)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'change_password.html')

    # Helper
    def _get_updated_self_user(self):
        return User.objects.get(username=self.user.username)
