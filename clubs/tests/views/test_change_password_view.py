"""Test user-facing implementation of the sign up form."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.forms import SignUpForm
from django.contrib.auth.hashers import check_password
from clubs.tests.helpers import LogInTester
from clubs.tests.helpers import reverse_with_next

class ChangePasswordViewTestCase(TestCase, LogInTester):
    def setUp(self):
        self.user = User.objects.create(
            first_name = "John",
            last_name = "Doe",
            email = "johndoe@example.org",
            password = 'Password123'
        )
        self.url = reverse('change_password')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_password_url(self):
        self.assertEqual(self.url, '/change_password/')

    # def test_get_password(self):
    #     self.client.login(username=self.user.username, password='Password123')
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'change_password.html')
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, PasswordChangeForm))

    def test_get_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_succesful_password_change(self):
    #     self.client.login(username=self.user.username, password='Password123')
    #     response = self.client.post(self.url, self.form_input, follow=True)
    #     response_url = reverse('change_password')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        # self.assertTemplateUsed(response, 'account.html')
        # self.user.refresh_from_db()
        # is_password_correct = check_password('NewPassword123', self.user.password)
        # self.assertTrue(is_password_correct)
