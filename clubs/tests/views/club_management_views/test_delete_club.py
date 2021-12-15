"""Test the delete club view."""

from django.test import TestCase
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from with_asserts.mixin import AssertHTMLMixin


class CreateClubViewTest(TestCase, MenuTesterMixin, AssertHTMLMixin):
    """Test all aspects of the delete club view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user_club_owner = User.objects.get(username='janedoe')
        self.user_club_officer = User.objects.get(username='richarddoe')
        self.user_club_member = User.objects.get(username='johndoe')

        self.club = Club.objects.get(name='King\'s Knights')

        # Owner of the club
        self.member_club_owner = Membership.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_owner = True,
        )

        # Officer of the club
        self.member_club_officer = Membership.objects.create(
            club = self.club,
            user = self.user_club_officer,
            is_officer = True,
        )

        # Standard member
        self.member = Membership.objects.create(
            club = self.club,
            user = self.user_club_member,
            is_owner = False,
            is_officer = False,
        )

        self.data = {
            'name' : 'Kings Knight',
            'location' : 'Kings College',
            'description' : 'best club in the world'
        }

        self.url = reverse('delete_club', kwargs = {'club_id': self.club.id})

    def test_delete_club_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/delete/')

    def test_get_delete_club_redirects_when_not_logged_in(self):
        response = self.client.post(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_delete_club_by_member_does_not_delete(self):
        self.client.login(email=self.user_club_member.email, password='Password123')

        club_count_before = Club.objects.count()
        member_count_before = Membership.objects.count()

        response = self.client.post(self.url, follow=True)

        club_count_after = Club.objects.count()
        member_count_after = Membership.objects.count()

        self.assertEqual(club_count_after, club_count_before)
        self.assertEqual(member_count_after, member_count_before)

        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club/show_club.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_delete_club_by_officer_does_not_delete(self):
        self.client.login(email=self.user_club_officer.email, password='Password123')

        club_count_before = Club.objects.count()
        member_count_before = Membership.objects.count()

        response = self.client.post(self.url, follow=True)

        club_count_after = Club.objects.count()
        member_count_after = Membership.objects.count()

        self.assertEqual(club_count_after, club_count_before)
        self.assertEqual(member_count_after, member_count_before)

        response_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club/show_club.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_successful_delete_club(self):
        self.client.login(email=self.user_club_owner.email, password='Password123')

        club_count_before = Club.objects.count()
        member_count_before = Membership.objects.count()

        response = self.client.post(self.url, follow=True)

        club_count_after = Club.objects.count()
        member_count_after = Membership.objects.count()

        self.assertEqual(club_count_after, club_count_before-1)
        self.assertEqual(member_count_after, 0)

        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'club/show_clubs.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)
