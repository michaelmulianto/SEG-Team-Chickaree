"""Test backend implementation of the ban viewer functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership, Application, Ban
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from with_asserts.mixin import AssertHTMLMixin
from django.conf import settings

class BannedMembersClubTestCase(TestCase, MenuTesterMixin):
    """Test all aspects of the show bans to club view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
    ]
    def setUp(self):
        self.user_club_owner = User.objects.get(username='johndoe')
        self.user_banned = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member_club_owner = Membership.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_owner = True
        )

        self.member_banned = Ban.objects.create(
            club=self.club,
            user=self.user_banned
        )

        self.url = reverse('banned_members', kwargs = {'club_id': self.club.id})

    def test_url_of_banned_members(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/banned_members/')

    def test_show_banned_members_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_banned_members_redirects_when_not_owner_of_club(self):
        self.client.login(email=self.user_banned.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_club', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_show_banned_members_redirects_when_invalid_club_id_entered(self):
        self.url = reverse('banned_members', kwargs = {'club_id': 999})
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_successful_show_banned_members(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'banned_member_list.html')

    def test_get_banned_members_of_my_club_list_with_pagination(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")
        self._create_test_ban_for_default_club(settings.BANNED_MEMBERS_PER_PAGE*2+3 -1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'banned_member_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['banned_members']), settings.BANNED_MEMBERS_PER_PAGE)
        banned_members_page = response.context['banned_members']
        self.assertFalse(banned_members_page.has_previous())
        self.assertTrue(banned_members_page.has_next())
        page_one_url = reverse('banned_members', kwargs = {'club_id': self.club.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'banned_member_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['banned_members']), settings.BANNED_MEMBERS_PER_PAGE)
        banned_members_page = response.context['banned_members']
        self.assertFalse(banned_members_page.has_previous())
        self.assertTrue(banned_members_page.has_next())
        page_two_url = reverse('banned_members', kwargs = {'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'banned_member_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['banned_members']), settings.BANNED_MEMBERS_PER_PAGE)
        banned_members_page = response.context['banned_members']
        self.assertTrue(banned_members_page.has_previous())
        self.assertTrue(banned_members_page.has_next())
        page_three_url = reverse('banned_members', kwargs = {'club_id': self.club.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'banned_member_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['banned_members']), 3)# plus one becase we have already banned a member
        banned_members_page = response.context['banned_members']
        self.assertTrue(banned_members_page.has_previous())
        self.assertFalse(banned_members_page.has_next())

    def test_show_banned_members_list_with_pagination_does_not_contain_page_traversers_if_not_enough_banned_members(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")
        self._create_test_ban_for_default_club(settings.BANNED_MEMBERS_PER_PAGE-2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'banned_member_list.html')
        self.assert_menu(response)
        banned_members_page = response.context['banned_members']
        self.assertFalse(banned_members_page.has_previous())
        self.assertFalse(banned_members_page.has_next())
        self.assertFalse(banned_members_page.has_other_pages())

    def _create_test_ban_for_default_club(self, banned_members_count = 10):
        for future_banned_member in range(banned_members_count):
            
            user = User.objects.create(
                username = f'USERNAME{future_banned_member}',
                last_name = f'LASTNAME{future_banned_member}',
                first_name = f'FIRSTNAME{future_banned_member}',
                email = f'EMAIL{future_banned_member}@gmail.com',
                bio = f'BIO{future_banned_member}',
                experience = 1
            )

            Ban.objects.create(
                club = self.club,
                user = user
            )