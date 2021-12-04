"""Test backend implementation of the ban viewer functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member, Application, Ban
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from with_asserts.mixin import AssertHTMLMixin

class ShowApplicationsToClubTestCase(TestCase, MenuTesterMixin):
    """Test all aspects of the show bans to club view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
    ]
    def setUp(self):
        self.user_club_owner = User.objects.get(username='johndoe')
        self.user_banned = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member_club_owner = Member.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_owner = True
        )

        self.member_banned = Ban.objects.create(
            club=self.club,
            user=self.user_banned
        )

        self.url = reverse('banned_members', kwargs = {'club_id': self.club.id})

    def test_url_of_banned_members(self):
        self.assertEqual(self.url, '/club/' + str(self.club.id) + '/banned_members')

    def test_show_banned_members_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_banned_members_redirects_when_not_owner_of_club(self):
        self.client.login(username=self.user_banned.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_show_banned_members_redirects_when_invalid_club_id_entered(self):
        self.url = reverse('banned_members', kwargs = {'club_id': 999})
        self.client.login(username=self.user_club_owner.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_successful_show_banned_members(self):
        self.client.login(username=self.user_club_owner.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'banned_member_list.html')
