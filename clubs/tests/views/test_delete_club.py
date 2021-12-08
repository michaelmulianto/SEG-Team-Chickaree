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

    fixtures = ['clubs/tests/fixtures/default_user.json',        
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.other_user = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')
        self.url = reverse('delete_club', kwargs = {'club_id': self.club.id})
        self.data = {
            'name' : 'Kings Knight',
            'location' : 'Kings College',
            'description' : 'best club in the world'
        }

    def test_delete_club_url(self):
        self.assertEqual(self.url, '/club/1/edit/delete')

    def test_get_delete_club_redirects_when_not_logged_in(self):
        response = self.client.post(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_delete_club(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(club=self.club, user=self.user)

        club_count_before = Club.objects.count()
        member_count_before = Membership.objects.count()

        response = self.client.post(self.url, follow=True)

        club_count_after = Club.objects.count()
        member_count_after = Membership.objects.count()

        self.assertEqual(club_count_after, club_count_before-1)
        self.assertEqual(member_count_after, member_count_before-1)

        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)


    def test_successful_club_deletion_deletes_memberships_of_the_club(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(club=self.club, user=self.user, is_owner=True)
        Membership.objects.create(club=self.club, user=self.other_user)

        club_count_before = Club.objects.count()
        member_count_before = Membership.objects.count()

        response = self.client.post(self.url)

        club_count_after = Club.objects.count()
        member_count_after = Membership.objects.count()

        self.assertEqual(club_count_after, club_count_before-1)
        self.assertEqual(member_count_after, member_count_before-2)

        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.INFO)

    def test_delete_club_by_non_owner_does_not_delete(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(club=self.club, user=self.user, is_owner=False)

        club_count_before = Club.objects.count()
        member_count_before = Membership.objects.count()

        response = self.client.post(self.url)

        club_count_after = Club.objects.count()
        member_count_after = Membership.objects.count()

        self.assertEqual(club_count_after, club_count_before)
        self.assertEqual(member_count_after, member_count_before)

        response_url = reverse('show_clubs')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

