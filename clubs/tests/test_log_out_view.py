"""Unit test for the log out view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from .helpers import LogInTester

class LogOutViewTestCase(TestCase, LogInTester):

    def setUp(self):
        self.url = reverse('log_out')
        self.form_input = {
            'username': '@johndoe',
            'password': 'Password123'
        }
        self.user = User.objects.create_user(
            '@johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            password = 'Password123',
            is_active=True
        )

    def test_get_log_in_url(self):
        self.assertEqual('/log_out/', self.url)

    def test_get_log_out(self):
        self.client.login(username='@johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow = True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())
