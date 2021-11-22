"""Test backend implementation of the application functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Application
from clubs.forms import CreateClubForm
from clubs.tests.helpers import reverse_with_next

class ApplyToClubViewTestCase(TestCase):
    """Test all aspects of the apply to club view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.create(
            name = 'Kings Knight',
            location = 'Kings College',
            description = 'best club in the world'
        )

        self.data = {
            'experience':1,
            'personalStatement':'Hello',
        }

        self.url = reverse('apply_to_club', kwargs = {'club_id': self.club.id})

    def test_get_apply_to_club(self):
        self.assertEqual(self.url, '/apply_to_club/' + str(self.club.id))

    def test_get_apply_to_club_redirects_when_not_logged_in(self):
        app_count_before = Application.objects.count()
<<<<<<< HEAD:clubs/tests/test_apply_to_club_view.py
        redirect_url = reverse('log_in')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

    def test_successful_apply(self):
=======

        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

    def test_successful_application_to_club(self):
>>>>>>> main:clubs/tests/views/test_apply_to_club_view.py
        self.client.login(username=self.user.username, password="Password123")
        app_count_before = Application.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before+1)
        
        # Should redirect user somewhere appropriate, indicating success.
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_apply_with_invalid_form_input(self):
        self.data['personalStatement'] = ''
        self.client.login(username=self.user.username, password="Password123")

        app_count_before = Application.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        app_count_after = Application.objects.count()

        self.assertEqual(app_count_after, app_count_before)
        
        # Should send user back to application form.
        self.assertEqual(response.status_code, 200) # not a redirect. Same page.
        self.assertTemplateUsed(response, 'apply_to_club.html')
