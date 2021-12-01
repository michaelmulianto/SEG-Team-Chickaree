"""Unit test for the account view"""

from django.http import response
from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin


class AccountViewTestCase(TestCase, MenuTesterMixin):
    """Test all aspects of the account view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('account')
        self.user = User.objects.get(username='johndoe')

    def test_get_account_url(self):
        self.assertEqual('/account/', self.url)

    def test_get_account_logged_in_user(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account.html')
        self.assert_menu(response)

    def test_get_account_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
