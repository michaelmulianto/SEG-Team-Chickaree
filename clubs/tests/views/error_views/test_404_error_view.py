"""Unit test for the 404 error page view"""
from django.test import TestCase, override_settings
from clubs.models import User
from clubs.tests.helpers import MenuTesterMixin
from system import urls

class Http404ErrorViewTestCase(TestCase, MenuTesterMixin):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = self.client.get('/clubs/ThisWillNotWork')
        self.user = User.objects.get(username='johndoe')

    @override_settings(DEBUG=False)
    def test_wrong_uri_returns_404(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'http404ErrorPage.html')

    @override_settings(DEBUG=False)
    def test_wrong_uri_returns_404_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'http404ErrorPage.html')
