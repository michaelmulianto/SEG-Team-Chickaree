"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User

class AccountViewTestCase(TestCase):
    """Test aspects of account view"""
    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.create_user(
            'johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            password = 'Password123',
            is_active=True
        )

    def test_get_home_url(self):
        self.assertEqual('/', self.url)

    def test_get_home_no_loggin_in_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_logged_in_user(self):
        # Log in and make sure the user is redirected to a different page
        self.client.login(username='johndoe', password='Password123')
        response_url = reverse('account')
        response = self.client.get(self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
