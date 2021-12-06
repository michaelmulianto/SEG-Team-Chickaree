"""Unit test for the show my clubs list"""

from typing import List
from django.core.paginator import Page
from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Member, Application
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.db.models.base import ObjectDoesNotExist 

class MyClubsListTestCase(TestCase, MenuTesterMixin):

    """Test aspects of my clubs view"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.url = reverse('my_clubs_list')
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

    def test_my_clubs_list_url(self):
        self.assertEqual(self.url, '/account/my_clubs/')

    def test_get_my_clubs_list(self):
        self.client.login(email=self.user.email, password = 'Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        clubs = response.context['clubs']
        current_user = response.context['current_user']
        page_obj = response.context['page_obj']
        self.assertTrue(isinstance(clubs, List))
        self.assertEqual(self.user, current_user)
        self.assertTrue(isinstance(page_obj, Page))
        self.assert_menu(response)

    def test_get_user_list_redirects_when_not_logged_in(self):
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

    def test_club_user_has_applied_is_on_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 0)

        Application.objects.create(
            club = self.club,
            user = self.user,
            personal_statement = 'I love chess!'
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 1)

    def test_club_user_has_not_applied_not_on_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 0)

    def test_make_new_application_makes_it_onto_the_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 0)

        self._make_new_membership(self.club, self.user)  
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 1)

    def test_withdraw_application_makes_club_not_on_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_clubs_list.html')
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 0)

        membership = self._make_new_membership(self.club, self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 1)

        Member.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        clubs = response.context['clubs']
        self.assertEqual(len(clubs), 0)

    #make a new membership for a user to a club
    def _make_new_membership(self, clubIn, userIn):
        membership = Member.objects.create(
        club = clubIn,
        user = userIn,
        is_officer = False,
        is_owner = False
        )
        return membership

    #check a club can be on the list
    def _is_on_list(self):
        try:
            Club.objects.get(name = self.club.name)
        except ObjectDoesNotExist:
            return 
        else:
            return True
