"""
Test backend implementation of the ability for officers or owners to unban members from
their club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership, Ban
from clubs.tests.helpers import reverse_with_next

class UnbanMemberViewTestCase(TestCase):
    """Test all aspects of the backend implementation of unbannning members from a club"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user_club_owner = User.objects.get(username='janedoe')
        self.user_club_officer = User.objects.get(username='richarddoe')
        self.user_being_unbanned = User.objects.get(username='johndoe')

        self.club = Club.objects.get(name='King\'s Knights')

        #Owner of the club
        Membership.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_officer = False,
            is_owner = True,
        )

        #An officer of the club
        Membership.objects.create(
            club = self.club,
            user = self.user_club_officer,
            is_officer = True,
            is_owner = False,
        )

        self.member_ban_being_unbanned = Ban.objects.create(
            club = self.club,
            user = self.user_being_unbanned,
        )

        self.url = reverse('unban_member', kwargs = {'ban_id': self.member_ban_being_unbanned.id})

    def test_unban_url(self):
        self.assertEqual(self.url, '/unban_member/' + str(self.member_ban_being_unbanned.id))

    def test_unban_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())

    def test_unban_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('unban_member', kwargs = {'ban_id': 999})
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())

    def test_unban_redirects_when_not_owner_or_officer(self): #Utilises the user bieng unban for test (a user being unban will never be an owner or ofificer)
        self.client.login(email=self.user_being_unbanned.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())

    def test_unban_redirects_as_officer(self):
        self.client.login(email=self.user_club_officer.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertFalse(self._has_member_been_unbanned())
        self.assertFalse(self._has_member_been_added())
        redirect_url = reverse('banned_members', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'banned_member_list.html')

    def test_successful_unban_as_owner(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('banned_members', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'banned_member_list.html')
        self.assertTrue(self._has_member_been_unbanned())
        self.assertTrue(self._has_member_been_added())

    def _has_member_been_unbanned(self):
        return not Ban.objects.filter(user=self.user_being_unbanned, club=self.club).exists()

    def _has_member_been_added(self):
        return Membership.objects.filter(user=self.user_being_unbanned, club=self.club).exists()
