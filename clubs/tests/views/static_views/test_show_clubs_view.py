"""Unit test for the view allowing a list of clubs to be fetched and displayed."""

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from clubs.models import Membership, User, Club
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.core.exceptions import ObjectDoesNotExist

class ShowClubsViewTestCase(TestCase, MenuTesterMixin):
    """Test aspects of the view that lists all clubs and acts as a home page"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json']


    def setUp(self):
        self.url = reverse('show_clubs')
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')


    def test_get_show_clubs_url(self):
        self.assertEqual(self.url, '/clubs/')

    def test_get_show_clubs(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)

    def test_get_show_clubs_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'account/log_in.html')

    def test_inexistent_club_is_cannot_be_on_list(self):
        self.club.name = "@@@BADCLUBNAME"
        self.assertFalse(self._is_on_list())

    def test_create_new_club_is_on_list(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        before_count = Club.objects.count()

        new_club = self._make_new_club()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)

        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count+1)
        self._club_is_on_list(new_club)

    def test_delete_club_is_no_longer_on_list(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        before_count1 = Club.objects.count()

        new_club = self._make_new_club_with_default_user_as_owner()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)

        after_count1 = Club.objects.count()
        self.assertEqual(after_count1, before_count1+1)
        self._club_is_on_list(new_club)
        before_count2 = Club.objects.count()

        self.client.post(reverse('delete_club', kwargs = {'club_id': new_club.id}))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        after_count2 = Club.objects.count()
        self.assertEqual(after_count2, before_count2-1)
        self._club_is_on_list(new_club)

    def test_get_show_clubs_with_pagination(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE*2+3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('show_clubs') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('show_clubs') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 3)
        page_obj = response.context['page_obj']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())

    
    def _create_test_clubs(self, club_count=10):
        for club_id in range(club_count):
            Club.objects.create(
                name = f'NEW_CLUB{club_id}',
                location = f'LOCATION {club_id}',
                description = f'DESCRIPTION {club_id}'
            )

    def _make_new_club(self):
        new_club_1 = Club.objects.create(
            name = "NEW_CLUB1",
            location = "London",
            description = "THIS IS AN AMAZING CHESS CLUB"
            )
        return new_club_1

    def _make_new_club_with_default_user_as_owner(self):
        new_club_2 = Club.objects.create(
        name = "NEW_CLUB2",
        location = "Parus",
        description = "THIS CHESS CLUBS IS BETTER"
        )

        Membership.objects.create(
        club = new_club_2,
        user = self.user,
        is_officer = False,
        is_owner = True
        )

        return new_club_2

    #check a club can be on the list
    def _is_on_list(self):
        try:
            Club.objects.get(name = self.club.name)
        except ObjectDoesNotExist:
            return False
        else:
            return True

    def _club_is_on_list(self, club):
        try:
            Club.objects.get(name = club.name)
        except ObjectDoesNotExist:
            return False
        else:
            return True
