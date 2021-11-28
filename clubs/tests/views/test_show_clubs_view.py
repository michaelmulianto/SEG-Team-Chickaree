"""Unit test for the view allowing a list of clubs to be fetched and displayed."""

from django.test import TestCase
from django.urls import reverse

class ShowClubsViewTestCase(TestCase):
    """Test aspects of show clubs view"""
    def setUp(self):
        self.url = reverse('show_clubs')

    def test_get_show_clubs_url(self):
        self.assertEqual('/clubs/', self.url)

    def test_show_clubs_request(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "show_clubs.html")
        self.assertEqual(response.status_code, 200) #OK