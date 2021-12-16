"""Test backend implementation of the application functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Application, Membership, Ban
from clubs.forms import ApplyToClubForm
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin

class ApplyToClubViewTestCase(TestCase, MenuTesterMixin):
    """Test all aspects of the apply to club view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club_owner = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')
        Membership.objects.create(
            user = self.club_owner,
            club = self.club,
            is_owner = True
        )
        self.data = {
            'personal_statement':'Hello',
        }


        self.url = reverse('apply_to_club', kwargs = {'club_id': self.club.id})

    def test_url_of_apply_to_club(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/apply/')

    def test_get_apply_to_club_redirects_when_not_logged_in(self):
        app_count_before = Application.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

    def test_get_apply_redirects_when_banned(self):
        self.client.login(email=self.user.email, password="Password123")

        Ban.objects.create(
            club = self.club,
            user = self.user,
        )

        app_count_before = Application.objects.count()
        response = self.client.get(self.url, follow=True)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')

    def test_get_apply(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'club/apply_to_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplyToClubForm))
        self.assertFalse(form.is_bound)
        self.assert_menu(response)

    def test_unsuccessful_application_when_already_applied(self):
        self.client.login(email=self.user.email, password="Password123")
        self.application = Application.objects.create(
            club = self.club,
            user = self.user,
            personal_statement = 'I love chess!'
        )

        app_count_before = Application.objects.count()
        response = self.client.post(self.url, self.data)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'club/apply_to_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplyToClubForm))
        self.assertTrue(form.is_bound)


    def test_unsuccessful_application_when_already_member(self):
        self.client.login(email=self.user.email, password="Password123")

        Membership.objects.create(
            club = self.club,
            user = self.user,
            is_owner = False
        )

        app_count_before = Application.objects.count()
        response = self.client.post(self.url, self.data)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'club/apply_to_club.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ApplyToClubForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_application_when_banned_and_redirect(self):
        self.client.login(email=self.user.email, password="Password123")

        Ban.objects.create(
            club = self.club,
            user = self.user,
        )

        app_count_before = Application.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')

    def test_apply_with_invalid_form_input(self):
        self.data['personal_statement'] = ''
        self.client.login(email=self.user.email, password="Password123")

        app_count_before = Application.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        app_count_after = Application.objects.count()

        self.assertEqual(app_count_after, app_count_before)

        # Should send user back to application form.
        self.assertEqual(response.status_code, 200) # not a redirect. Same page.
        self.assertTemplateUsed(response, 'club/apply_to_club.html')

    def test_successful_application(self):
        self.client.login(email=self.user.email, password="Password123")
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
        self.assertTemplateUsed(response, 'club/show_clubs.html')
