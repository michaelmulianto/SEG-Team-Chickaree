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
        self.user_club_owner = User.objects.get(username='janedoe')
        self.user_club_officer = User.objects.get(username='richarddoe')
        self.user_being_kicked = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member_club_owner = Membership.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_owner = True,
        )
        self.member_club_officer = Membership.objects.create(
            club = self.club,
            user = self.user_club_officer,
            is_officer = True,
        )

        self.member_being_kicked = Membership.objects.create(
            club = self.club,
            user = self.user_being_kicked,
        )

        self.url = reverse('kick_member', kwargs = {'member_id': self.member_being_kicked.id})
        self.url_kick_an_officer = reverse('kick_member', kwargs = {'member_id': self.member_club_officer.id})
        self.url_kick_the_owner = reverse('kick_member', kwargs = {'member_id': self.member_club_owner.id})

    def test_kick_url(self):
        self.assertEqual(self.url, f'/member/{self.member_being_kicked.id}/kick/')
        self.assertEqual(self.url_kick_an_officer, f'/member/{self.member_club_officer.id}/kick/')
        self.assertEqual(self.url_kick_the_owner, f'/member/{self.member_club_owner.id}/kick/')

    def test_kick_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_kicked(self.member_being_kicked))

    def test_kick_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('kick_member', kwargs = {'member_id': 999})
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assertFalse(self._has_member_been_kicked(self.member_being_kicked))

    def test_kick_redirects_when_not_owner_or_officer_of_club(self):
        self.client.login(email=self.user_being_kicked.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertFalse(self._has_member_been_kicked(self.member_being_kicked))

    def test_kick_redirects_when_kicking_officer(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url_kick_an_officer, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertFalse(self._has_member_been_kicked(self.member_club_officer))

    def test_kick_redirects_when_kicking_owner(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url_kick_the_owner, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertFalse(self._has_member_been_kicked(self.member_club_owner))

    def test_successful_kick_as_officer(self):
        self.client.login(email=self.user_club_officer.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertTrue(self._has_member_been_kicked(self.member_being_kicked))
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')

    def test_successful_kick_as_owner(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertTrue(self._has_member_been_kicked(self.member_being_kicked))

    def _has_member_been_kicked(self, member):
        return not Membership.objects.filter(id=member.id).exists()
