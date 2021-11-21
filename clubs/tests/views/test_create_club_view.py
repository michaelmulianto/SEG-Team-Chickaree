"""Test user-facing implementation of the create club form."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club
from clubs.forms import CreateClubForm
from clubs.tests.helpers import reverse_with_next


class CreateClubViewTest(TestCase):
    """Test all aspects of the create club view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('create_club')
        self.user = User.objects.get(username='johndoe')
        self.data = {
        'name' : 'Kings Knight',
        'location' : 'Kings College',
        'description' : 'best club in the world'
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, '/create_club/')

    def test_get_create_club_loads_empty_form(self):
        self.client.login(username=self.user.username, password="Password123")
        user_count_before = Club.objects.count()
        response = self.client.get(self.url, follow=True)
        user_count_after = Club.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertEqual(response.status_code, 200)

    def test_get_create_club_redirects_when_not_logged_in(self):
        response = self.client.post(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_create_club(self):
        self.client.login(username=self.user.username, password="Password123")
        user_count_before = Club.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Club.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_club = Club.objects.latest('created_on')
        #self.assertEqual(self.user, new_post.author)
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_unsuccessful_create_club(self):
        self.client.login(username='johndoe', password='Password123')
        club_count_before = Club.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        club_count_after = Club.objects.count()
        self.assertEqual(club_count_after, club_count_before)
        self.assertTemplateUsed(response, 'create_club.html')