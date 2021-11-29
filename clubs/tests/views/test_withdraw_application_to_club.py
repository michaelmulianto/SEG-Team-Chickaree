"""Test backend implementation of the application functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Application, Member
from clubs.tests.helpers import reverse_with_next

class WithdrawApplicationToClubTestCase(TestCase):
    """Test all aspects of withdrawing an application to a club"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')
        self.application = Application.objects.create(
            club = self.club,
            user = self.user,
            experience = 2,
            personal_statement = 'I love chess!'
        )

        self.url = reverse('withdraw_application_to_club', kwargs = {'club_id': self.club.id})

    def test_url_of_withdraw_application_to_club(self):
        self.assertEqual(self.url, '/withdraw_application_to_club/' + str(self.club.id))

    def test_withdraw_application_to_club_redirects_when_not_logged_in(self):
        app_count_before = Application.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

    def test_unsuccessful_withdrawal_when_not_applied(self):
        self.client.login(username=self.user.username, password="Password123")
        Application.objects.get(club=self.club, user=self.user).delete()

        app_count_before = Application.objects.count()
        response = self.client.post(self.url, follow=True)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')


    def test_unsuccessful_withdrawal_when_already_member(self):
        self.client.login(username=self.user.username, password="Password123")
        self.membership = Member.objects.create(
            club = self.club,
            user = self.user,
            is_owner = False
        )

        app_count_before = Application.objects.count()
        response = self.client.post(self.url, follow=True)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before)

        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_successful_application(self):
        self.client.login(username=self.user.username, password="Password123")
        app_count_before = Application.objects.count()
        response = self.client.post(self.url, follow=True)
        app_count_after = Application.objects.count()
        self.assertEqual(app_count_after, app_count_before-1)

        # Should redirect user somewhere appropriate, indicating success.
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
