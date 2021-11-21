"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User

class AccountViewTestCase(TestCase):
    """Test aspects of account view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(username='johndoe')

    def test_get_home_url(self):
        self.assertEqual('/', self.url)

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('account')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'account.html')

    def test_get_home_logged_in_user(self):
        # Log in and make sure the user is redirected to a different page
        self.client.login(username='johndoe', password='Password123')
        response_url = reverse('account')
        response = self.client.get(self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
