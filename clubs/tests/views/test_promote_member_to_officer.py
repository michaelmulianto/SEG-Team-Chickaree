"""
Test backend implementation of the ability for owners to promote members of
their club to an officer of said club.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member
from clubs.tests.helpers import reverse_with_next

class PromoteMemberToOfficerViewTestCase(TestCase):
    """Test all aspects of the backend implementation of promoting members"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/second_user.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.ownerUser = User.objects.get(username='johndoe')
        self.targetUser = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.ownerMember = Member.objects.create(
            club = self.club,
            user = self.ownerUser,
            is_owner = True
        )

        self.targetMember = Member.objects.create(
            club = self.club,
            user = self.ownerUser,
            is_owner = False,
            is_officer = False,
        )

        self.url = reverse('promote_member_to_officer', kwargs = {'club_id': self.club.id, 'member_id': self.targetMember.id})

    def test_promote_url(self):
        self.assertEqual(self.url, '/club/' + str(self.club.id) + '/promote_member/' + str(self.targetMember.id))

    def test_promote_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertEqual(Member.objects.get(id=self.targetMember.id).is_officer, False)

    def test_promote_redirects_when_not_owner_of_club(self):
        self.ownerMember.is_owner = False
        self.ownerMember.save(update_fields=['is_owner'])

        self.client.login(username=self.ownerUser.username, password="Password123")
        response = self.client.get(self.url, follow=True)

        redirect_url = reverse('show_club', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')
        self.assertEqual(Member.objects.get(id=self.targetMember.id).is_officer, False)

    def test_promote_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('promote_member_to_officer', kwargs = {'club_id': self.club.id, 'member_id':int(self.targetMember.id-1)})
        self.client.login(username=self.ownerUser.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertEqual(Member.objects.get(id=self.targetMember.id).is_officer, False)

    def test_promote_redirects_when_invalid_club_id_entered(self):
        self.url = reverse('promote_member_to_officer', kwargs = {'club_id': self.club.id-1, 'member_id':self.targetMember.id})
        self.client.login(username=self.ownerUser.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertEqual(Member.objects.get(id=self.targetMember.id).is_officer, False)

    def test_successful_promotion(self):
        self.client.login(username=self.ownerUser.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(Member.objects.get(id=self.targetMember.id).is_officer, True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
