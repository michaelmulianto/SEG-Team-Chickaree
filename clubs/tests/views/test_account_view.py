"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import reverse_with_next

class AccountViewTestCase(TestCase):
    """To be implemented, code stolen from clucker, change feed for account and edit"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('account')
        self.user = User.objects.get(username='johndoe')
        self.client.login(username='johndoe', password='Password123')

    def test_get_account_url(self):
        self.assertEqual('/account/', self.url)

    def test_get_account_logged_in_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account.html')

    def test_get_account_redirects_when_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)