"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User

class AccountViewTestCase(TestCase):
    """To be implemented, code stolen from clucker, change feed for account and edit"""

    def setUp(self):
        self.url = reverse('account')
        self.user = User.objects.create_user(
            'johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            password = 'Password123',
            is_active=True
        )
        self.client.login(username='johndoe', password='Password123')


    def test_get_account_url(self):
        self.assertEqual('/account/', self.url)

    def test_get_account_logged_in_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account.html')

    def test_user_not_logged_in_cannot_see_account_details(self):
        self.client.logout()
        response = self.client.post(self.url, follow = True)
        response_url = reverse("home")
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        #log back in just in case for other tests
        self.client.login(username='@johndoe', password='Password123')
