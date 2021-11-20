"""Test backend implementation of the application functionality."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Application
from clubs.forms import CreateClubForm
from django.contrib.auth.hashers import check_password

class ApplyToClubViewTestCase(TestCase):
    """Test all aspects of the apply to club view"""

    def setUp(self):
        self.user = User.objects.create_user(
            'johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )
        self.club = Club.objects.create(
            name = 'Kings Knight',
            location = 'Kings College',
            description = 'best club in the world'
        )

        self.url = reverse('apply_to_club', kwargs = {'club_id': self.club.id})

    def test_apply_to_club_url(self):
        self.assertEqual(self.url, '/apply_to_club/' + str(self.club.id))

    def test_apply_to_club_redirects_when_not_logged_in(self):
        app_count_before = Application.objects.count()
        redirect_url = reverse('log_in')
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

    def test_successful_apply(self):
        self.client.login(username=self.user.username, password="Password123")
        app_count_before = Application.objects.count()
        response = self.client.post(self.url, follow=True)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before+1)
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
