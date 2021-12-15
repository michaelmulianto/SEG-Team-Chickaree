"""
Test backend implementation of the ability for owners to demote members of
their club to an officer of said club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next

class DemoteOfficerToMemberViewTestCase(TestCase):
    """Test all aspects of the backend implementation of demoting members"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.owner_user = User.objects.get(username='johndoe')
        self.non_officer_user = User.objects.get(username='richarddoe')
        self.target_user = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
        )

        self.non_officer_member = Membership.objects.create(
            club = self.club,
            user = self.non_officer_user,
        )

        self.target_member = Membership.objects.create(
            club = self.club,
            user = self.target_user,
            is_officer = True,
        )

        self.url = reverse('demote_officer_to_member', kwargs = {'member_id': self.target_member.id})

    def test_demote_url(self):
        self.assertEqual(self.url, f'/member/{self.target_member.id}/demote/')

    def test_demote_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_demoted(self.target_member.id))

    def test_demote_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('demote_officer_to_member', kwargs = {'member_id': 999})
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assertFalse(self._has_member_been_demoted(self.target_member.id))

    def test_demote_redirects_when_not_owner_of_club(self):
        self.client.login(email=self.non_officer_user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertFalse(self._has_member_been_demoted(self.target_member.id))

    def test_demote_redirects_when_owner_demoting_themselves(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        url_demote_owner = reverse('demote_officer_to_member', kwargs = {'member_id': self.owner_member.id})
        response = self.client.get(url_demote_owner, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertTrue(self._has_member_been_demoted(self.owner_member.id))

    def test_demote_redirects_when_demoting_non_officer(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        url_demote_member = reverse('demote_officer_to_member', kwargs = {'member_id': self.non_officer_member.id})
        response = self.client.get(url_demote_member, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertTrue(self._has_member_been_demoted(self.non_officer_member.id))

    def test_successful_demotion(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.assertFalse(self._has_member_been_demoted(self.target_member.id))
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertTrue(self._has_member_been_demoted(self.target_member.id))

    def _has_member_been_demoted(self, member_id):
        return not Membership.objects.get(id=member_id).is_officer
