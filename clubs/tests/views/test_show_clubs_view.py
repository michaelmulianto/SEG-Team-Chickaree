"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from clubs.models import User
from clubs.tests.helpers import reverse_with_next

class ShowClubsViewTestCase(TestCase):
    """Test aspects of the view that lists all clubs and acts as a home page"""

    fixtures = ['clubs/tests/fixtures/default_user.json']


    def setUp(self):
        self.url = reverse('show_clubs')
        self.user = User.objects.get(username='johndoe')

    def test_get_show_clubs_url(self):
        self.assertEqual('/show_clubs/' , self.url)

    def test_get_show_clubs(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_get_show_clubs_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'log_in.html')
