"""
Test backend implementation of the ability for owners to promote members of
their club to an officer of said club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next

class PromoteMemberToOfficerViewTestCase(TestCase):
    """Test all aspects of the backend implementation of promoting members"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.owner_user = User.objects.get(username='johndoe')
        self.officer_user = User.objects.get(username='richarddoe')
        self.target_user = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
        )
        self.officer_member = Membership.objects.create(
            club = self.club,
            user = self.officer_user,
            is_officer = True,
        )

        self.target_member = Membership.objects.create(
            club = self.club,
            user = self.target_user,
            is_owner = False,
            is_officer = False,
        )

        self.url = reverse('promote_member_to_officer', kwargs = {'member_id': self.target_member.id})

    def test_promote_url(self):
        self.assertEqual(self.url, f'/member/{self.target_member.id}/promote/')

    def test_promote_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._has_member_been_promoted(self.target_member.id))

    def test_promote_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('promote_member_to_officer', kwargs = {'member_id': 999})
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assertFalse(self._has_member_been_promoted(self.target_member.id))

    def test_promote_redirects_when_not_owner_of_club(self):
        self.client.login(email=self.target_user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertFalse(self._has_member_been_promoted(self.target_member.id))

    def test_promote_redirects_when_owner_promoting_themselves(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        url_promote_owner = reverse('promote_member_to_officer', kwargs = {'member_id': self.owner_member.id})
        response = self.client.get(url_promote_owner, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertFalse(self._has_member_been_promoted(self.owner_member.id))

    def test_promote_redirects_when_promoting_officer(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        url_promote_officer = reverse('promote_member_to_officer', kwargs = {'member_id': self.officer_member.id})
        response = self.client.get(url_promote_officer, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertTrue(self._has_member_been_promoted(self.officer_member.id))

    def test_successful_promotion(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.assertFalse(self._has_member_been_promoted(self.target_member.id))
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assertTrue(self._has_member_been_promoted(self.target_member.id))

    def _has_member_been_promoted(self, member_id):
        return Membership.objects.get(id=member_id).is_officer
