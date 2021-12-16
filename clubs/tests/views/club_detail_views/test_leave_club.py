"""Test backend implementation of the leaving club functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next

class LeaveClubTestCase(TestCase):
    """Test all aspects of leaving a club"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.user_club_owner = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')
        Membership.objects.create(
            club = self.club,
            user = self.user
        )
        Membership.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_owner = True
        )

        self.url = reverse('leave_club', kwargs = {'club_id': self.club.id})

    def test_url_of_leave_club(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/leave/')

    def test_leave_club_redirects_when_not_logged_in(self):
        member_count_before = Membership.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        member_count_after = Membership.objects.count()
        self.assertEqual(member_count_after, member_count_before)

    def test_leave_redirects_when_invalid_club_id_entered(self):
        url_invalid_id = reverse('leave_club', kwargs = {'club_id': 999})
        self.client.login(email=self.user_club_owner.email, password="Password123")
        member_count_before = Membership.objects.count()
        response = self.client.get(url_invalid_id, follow=True)
        member_count_after = Membership.objects.count()
        self.assertEqual(member_count_after, member_count_before)

        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club/show_clubs.html')


    def test_unsuccessful_leave_when_not_member(self):
        self.client.login(email=self.user.email, password="Password123")
        Membership.objects.get(club=self.club, user=self.user).delete()

        member_count_before = Membership.objects.count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Membership.objects.count()
        self.assertEqual(member_count_after, member_count_before)

        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club/show_club.html')

    def test_unsuccessful_leave_when_club_owner(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")

        member_count_before = Membership.objects.count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Membership.objects.count()
        self.assertEqual(member_count_after, member_count_before)

        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club/show_club.html')

    def test_successful_leave(self):
        self.client.login(email=self.user.email, password="Password123")
        member_count_before = Membership.objects.count()
        response = self.client.get(self.url, follow=True)
        member_count_after = Membership.objects.count()
        self.assertEqual(member_count_after, member_count_before-1)

        # Should redirect user somewhere appropriate, indicating success.
        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club/show_clubs.html')
