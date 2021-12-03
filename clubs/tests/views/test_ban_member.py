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
        'clubs/tests/fixtures/other_users.json',
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
        self.member_club_officer = Member.objects.create(
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

        self.url_ban = reverse('ban_member', kwargs = {'member_id': self.member_being_banned.id})
        self.url_ban_an_officer = reverse('ban_member', kwargs = {'member_id': self.member_club_officer.id})

    def test_ban_urls(self):
        self.assertEqual(self.url_ban, '/ban_member/' + str(self.member_being_banned.id))
        self.assertEqual(self.url_ban_an_officer, '/ban_member/' + str(self.member_club_officer.id))

    def test_ban_redirects_when_not_logged_in(self):
        response = self.client.get(self.url_ban)
        redirect_url = reverse_with_next('log_in', self.url_ban)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_banned(self.user_being_banned, self.club))
        self.assertFalse(self._has_member_been_kicked(self.member_being_banned))

    def test_ban_redirects_when_invalid_member_id_entered(self):
        self.url_ban = reverse('ban_member', kwargs = {'member_id': 999})
        self.client.login(username=self.user_club_owner.username, password="Password123")
        response = self.client.get(self.url_ban, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._has_member_been_banned(self.user_being_banned, self.club))
        self.assertFalse(self._has_member_been_kicked(self.member_being_banned))

    def test_ban_redirects_when_not_owner_or_officer(self): #Utilises the user bieng ban for test (a user being ban will never be an owner or ofificer)
        self.client.login(username=self.user_being_banned.username, password="Password123")
        response = self.client.get(self.url_ban, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertFalse(self._has_member_been_banned(self.user_being_banned, self.club))
        self.assertFalse(self._has_member_been_kicked(self.member_being_banned))

    def test_ban_redirects_as_officer(self):
        self.client.login(username=self.user_club_officer.username, password="Password123")
        response = self.client.get(self.url_ban, follow=True)
        self.assertFalse(self._has_member_been_banned(self.user_being_banned, self.club))
        self.assertFalse(self._has_member_been_kicked(self.member_being_banned))
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')

    def test_ban_redirects_if_member_is_officer(self):
        self.client.login(username=self.user_club_owner.username, password="Password123")
        response = self.client.get(self.url_ban_an_officer, follow=True)
        self.assertFalse(self._has_member_been_banned(self.user_club_officer, self.club))
        self.assertFalse(self._has_member_been_kicked(self.member_club_officer))
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')

    def test_successful_ban_as_owner(self):
        self.client.login(username=self.user_club_owner.username, password="Password123")
        response = self.client.get(self.url_ban, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._has_member_been_banned(self.user_being_banned, self.club))
        self.assertTrue(self._has_member_been_kicked(self.member_being_banned))

    def _has_member_been_banned(self, user, club):
        return Ban.objects.filter(user=user, club=club).exists()

    def _has_member_been_kicked(self, member):
        return not Member.objects.filter(id=member.id).exists()
