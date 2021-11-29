"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

class ShowClubsViewTestCase(TestCase):
    """Test aspects of account view"""
    def setUp(self):
        self.url = reverse('show_clubs')

    def test_get_show_clubs_url(self):
        self.assertEqual('/show_clubs/' , self.url)
