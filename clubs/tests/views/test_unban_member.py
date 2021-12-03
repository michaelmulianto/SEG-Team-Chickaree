"""
Test backend implementation of the ability for officers or owners to unban members from
their club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member, Ban
from clubs.tests.helpers import reverse_with_next

class UnbanMemberViewTestCase(TestCase):
    """Test all aspects of the backend implementation of unbanning members from a club"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/second_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user_unbanning = User.objects.get(username='janedoe')
        self.user_being_unbanned = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member_unbanning = Member.objects.create(
            club = self.club,
            user = self.user_unbanning,
            is_officer = False,
            is_owner = False,
        )

        self.member_being_unbanned = Ban.objects.create(
            club = self.club,
            user = self.user_being_unbanned,
        )

        self.url = reverse('unban_member', kwargs = {'ban_id': self.member_being_unbanned.id})

    def test_unban_url(self):
        self.assertEqual(self.url, '/unban_member/' + str(self.member_being_unbanned.id))

    def test_unban_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())

    def test_unban_redirects_when_invalid_ban_id_entered(self):
        self.url = reverse('unban_member', kwargs = {'ban_id': 999})
        self.client.login(username=self.user_unbanning.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())

    def test_unban_redirects_when_not_owner_or_officer(self):
        self.client.login(username=self.user_unbanning.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())

    def test_unban_redirects_as_officer(self):
        self.member_unbanning.is_officer = True
        self.member_unbanning.save()
        self.client.login(username=self.user_unbanning.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')

    def test_successful_unban_as_owner(self):
        self.member_unbanning.is_owner = True
        self.member_unbanning.save()
        self.client.login(username=self.user_unbanning.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._has_member_been_unbanned())
        self.assertTrue(self._has_member_been_added())

    def _has_member_been_unbanned(self):
        return not Ban.objects.filter(user=self.user_being_unbanned, club=self.club).exists()

    def _has_member_been_added(self):
        return Member.objects.filter(id=self.member_being_unbanned.id).exists()
