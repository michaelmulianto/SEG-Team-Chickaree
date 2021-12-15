"""Unit test for the show my clubs list"""

from typing import List
from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership, Application
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class MyClubsListTestCase(TestCase, MenuTesterMixin):

    """Test aspects of my clubs view"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.url = reverse('my_clubs_list')
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

    def test_my_clubs_list_url(self):
        self.assertEqual(self.url, '/clubs/my/')

    def test_get_my_clubs_list(self):
        self.client.login(email=self.user.email, password = 'Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        current_user = response.context['current_user']
        # note: my_clubs_list holds the clubs on the list
        my_clubs_list = response.context['my_clubs']
        for club in my_clubs_list:
            self.assertTrue(isinstance(club, List))
        self.assertEqual(self.user, current_user)
        self.assertTrue(isinstance(my_clubs_list, Page))
        self.assert_menu(response)

    def test_get_my_clubs_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_inexistent_club_is_cannot_be_on_list(self):
        self.club.name = "@@@BADCLUBNAME"
        self.assertFalse(self._is_on_list())

    def test_get_my_clubs_on_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)

    def test_club_user_has_applied_is_on_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 0)

        Application.objects.create(
            club = self.club,
            user = self.user,
            personal_statement = 'I love chess!'
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 1)

    def test_club_user_has_not_applied_not_on_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 0)

    def test_make_new_application_makes_it_onto_the_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 0)

        self._make_new_membership(self.club, self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 1)

    def test_withdraw_application_makes_club_not_on_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 0)

        self._make_new_membership(self.club, self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 1)

        Membership.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertEqual(len(my_clubs_page), 0)

    def test_get_my_clubs_list_for_applications_with_pagination(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs_and_apply_default_user(settings.CLUBS_PER_PAGE*2+3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), settings.CLUBS_PER_PAGE)
        my_clubs_page = response.context['my_clubs']
        self.assertFalse(my_clubs_page.has_previous())
        self.assertTrue(my_clubs_page.has_next())
        page_one_url = reverse('my_clubs_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), settings.CLUBS_PER_PAGE)
        my_clubs_page = response.context['my_clubs']
        self.assertFalse(my_clubs_page.has_previous())
        self.assertTrue(my_clubs_page.has_next())
        page_two_url = reverse('my_clubs_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), settings.CLUBS_PER_PAGE)
        my_clubs_page = response.context['my_clubs']
        self.assertTrue(my_clubs_page.has_previous())
        self.assertTrue(my_clubs_page.has_next())
        page_three_url = reverse('my_clubs_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), 3)
        my_clubs_page = response.context['my_clubs']
        self.assertTrue(my_clubs_page.has_previous())
        self.assertFalse(my_clubs_page.has_next())

    def test_get_my_clubs_list_for_memberships_with_pagination(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs_and_make_member_default_user(settings.CLUBS_PER_PAGE*2+3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), settings.CLUBS_PER_PAGE)
        my_clubs_page = response.context['my_clubs']
        self.assertFalse(my_clubs_page.has_previous())
        self.assertTrue(my_clubs_page.has_next())
        page_one_url = reverse('my_clubs_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), settings.CLUBS_PER_PAGE)
        my_clubs_page = response.context['my_clubs']
        self.assertFalse(my_clubs_page.has_previous())
        self.assertTrue(my_clubs_page.has_next())
        page_two_url = reverse('my_clubs_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), settings.CLUBS_PER_PAGE)
        my_clubs_page = response.context['my_clubs']
        self.assertTrue(my_clubs_page.has_previous())
        self.assertTrue(my_clubs_page.has_next())
        page_three_url = reverse('my_clubs_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['my_clubs']), 3)
        my_clubs_page = response.context['my_clubs']
        self.assertTrue(my_clubs_page.has_previous())
        self.assertFalse(my_clubs_page.has_next())

    def test_show_my_clubs_list_with_pagination_does_not_contain_page_traversers_if_not_enough_clubs(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs_and_apply_default_user(settings.CLUBS_PER_PAGE-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        self.assert_menu(response)
        my_clubs_page = response.context['my_clubs']
        self.assertFalse(my_clubs_page.has_previous())
        self.assertFalse(my_clubs_page.has_next())
        self.assertFalse(my_clubs_page.has_other_pages())

    def _create_test_clubs_and_apply_default_user(self, club_count=10):
        for club_id in range(club_count):

            Application.objects.create(
                club = Club.objects.create(
                    name = f'NEW_CLUB{club_id}',
                    location = f'LOCATION {club_id}',
                    description = f'DESCRIPTION {club_id}'
                    ),
                user = self.user,
                personal_statement = f'PERSONAL STATEMENT FOR CLUB {club_id}'
            )

    def _create_test_clubs_and_make_member_default_user(self, club_count=10):
        for club_id in range(club_count):

            Membership.objects.create(
                club = Club.objects.create(
                    name = f'NEW_CLUB{club_id}',
                    location = f'LOCATION {club_id}',
                    description = f'DESCRIPTION {club_id}'
                    ),
                user = self.user,
            )

    #make a new membership for a user to a club
    def _make_new_membership(self, clubIn, userIn):
        Membership.objects.create(
        club = clubIn,
        user = userIn,
        is_officer = False,
        is_owner = False
        )

    #check a club can be on the list
    def _is_on_list(self):
        try:
            Club.objects.get(name = self.club.name)
        except ObjectDoesNotExist:
            return False
        else:
            return True
