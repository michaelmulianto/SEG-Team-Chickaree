"""
Test backend implementation of the ability for officers or owners to kick members from
their club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next

class KickMemberViewTestCase(TestCase):
    """Test all aspects of the backend implementation of kicking members from a club"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user_kicking = User.objects.get(username='janedoe')
        self.user_being_kicked = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member_kicking = Membership.objects.create(
            club = self.club,
            user = self.user_kicking,
            is_officer = False,
            is_owner = False,
        )

        self.member_being_kicked = Membership.objects.create(
            club = self.club,
            user = self.user_being_kicked,
            is_owner = False,
            is_officer = False,
        )

        self.url = reverse('kick_member', kwargs = {'member_id': self.member_being_kicked.id})

    def test_kick_url(self):
        self.assertEqual(self.url, f'/member/{self.member_being_kicked.id}/kick/')

    def test_promote_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_kicked())

    def test_promote_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('kick_member', kwargs = {'member_id': 999})
        self.client.login(email=self.user_kicking.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._has_member_been_kicked())

    def test_promote_redirects_when_not_owner_or_officer_of_club(self):
        self.client.login(email=self.user_kicking.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertFalse(self._has_member_been_kicked())

    def test_successful_kick_as_officer(self):
        self.member_kicking.is_officer = True
        self.member_kicking.save()
        self.client.login(email=self.user_kicking.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertTrue(self._has_member_been_kicked())
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')

    def test_successful_kick_as_owner(self):
        self.member_kicking.is_owner = True
        self.member_kicking.save()
        self.client.login(email=self.user_kicking.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._has_member_been_kicked())

    def _has_member_been_kicked(self):
        return (not Membership.objects.filter(id=self.member_being_kicked.id).exists())
