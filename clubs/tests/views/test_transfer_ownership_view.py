"""
Test backend implementation of the ability for owners to transfer ownership
of their club to an officer of said club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member
from clubs.tests.helpers import reverse_with_next

class PromoteMemberToOfficerViewTestCase(TestCase):
    """Test all aspects of the backend implementation of transfering ownership."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/second_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.owner_user = User.objects.get(username='johndoe')
        self.target_user = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Member.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
        )

        self.target_member = Member.objects.create(
            club = self.club,
            user = self.target_user,
            is_officer = True,
        )

        self.url = reverse('transfer_ownership_to_officer', kwargs = {'member_id': self.target_member.id})

    def test_transfer_url(self):
        self.assertEqual(self.url, '/transfer_ownership_to/' + str(self.target_member.id))

    def test_transfer_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_ownership_been_transferred())

    def test_transfer_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('promote_member_to_officer', kwargs = {'member_id': 999})
        self.client.login(username=self.owner_user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._has_ownership_been_transferred())

    def test_transfer_redirects_when_not_owner_of_club(self):
        self.client.login(username=self.target_user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertFalse(self._has_ownership_been_transferred())

    def test_successful_transfer(self):
        self.client.login(username=self.owner_user.username, password="Password123")
        self.assertFalse(self._has_ownership_been_transferred())
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._has_ownership_been_transferred())

    def _has_ownership_been_transferred(self):
        return Member.objects.get(id=self.target_member.id).is_owner and not(Member.objects.get(id=self.owner_member.id).is_owner)