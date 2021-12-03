"""
Test backend implementation of the ability for officers or owners to ban members from
their club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member, Ban
from clubs.tests.helpers import reverse_with_next

class BanMemberViewTestCase(TestCase):
    """Test all aspects of the backend implementation of bannning members from a club"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/second_user.json',
        'clubs/tests/fixtures/third_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user_club_owner = User.objects.get(username='janedoe')
        self.user_club_officer = User.objects.get(username='richarddoe')
        self.user_being_banned = User.objects.get(username='johndoe')

        self.club = Club.objects.get(name='King\'s Knights')

        #Owner of the club
        Member.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_officer = False,
            is_owner = True,
        )

        #Officer of the club
        Member.objects.create(
            club = self.club,
            user = self.user_club_officer,
            is_officer = True,
            is_owner = False,
        )

        self.member_being_banned = Member.objects.create(
            club = self.club,
            user = self.user_being_banned,
            is_owner = False,
            is_officer = False,
        )

        self.url = reverse('ban_member', kwargs = {'member_id': self.member_being_banned.id})

    def test_kick_url(self):
        self.assertEqual(self.url, '/ban_member/' + str(self.member_being_banned.id))

    def test_ban_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_banned())
        self.assertFalse(self._has_member_been_kicked())

    def test_ban_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('ban_member', kwargs = {'member_id': 999})
        self.client.login(username=self.user_club_owner.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._has_member_been_banned())
        self.assertFalse(self._has_member_been_kicked())

    def test_ban_redirects_when_not_owner_or_officer(self): #Utilises the user bieng ban for test (a user being ban will never be an owner or ofificer)
        self.client.login(username=self.user_being_banned.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertFalse(self._has_member_been_banned())
        self.assertFalse(self._has_member_been_kicked())

    def test_ban_redirects_as_officer(self):
        self.client.login(username=self.user_club_officer.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertFalse(self._has_member_been_banned())
        self.assertFalse(self._has_member_been_kicked())
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')

    def test_successful_kick_as_owner(self):
        self.client.login(username=self.user_club_owner.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._has_member_been_banned())
        self.assertTrue(self._has_member_been_kicked())

    def _has_member_been_banned(self):
        return Ban.objects.filter(user=self.user_being_banned, club=self.club).exists()

    def _has_member_been_kicked(self):
        return (not Member.objects.filter(id=self.member_being_banned.id).exists())
