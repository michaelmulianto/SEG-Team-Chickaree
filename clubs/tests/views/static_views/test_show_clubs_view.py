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
        self.form_input = {
            'searched' : "",
        }
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
        clubs_page = response.context['page_obj']
        self.assertFalse(clubs_page.has_previous())
        self.assertTrue(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_one_url = reverse('show_clubs') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE)
        clubs_page = response.context['page_obj']
        self.assertFalse(clubs_page.has_previous())
        self.assertTrue(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE)
        clubs_page = response.context['page_obj']
        self.assertTrue(clubs_page.has_previous())
        self.assertTrue(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_three_url = reverse('show_clubs') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 3)
        clubs_page = response.context['page_obj']
        self.assertTrue(clubs_page.has_previous())
        self.assertFalse(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_clubs_with_pagination_does_not_contain_page_traversers_if_not_enough_clubs(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE-2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        clubs_page = response.context['page_obj']
        self.assertFalse(clubs_page.has_previous())
        self.assertFalse(clubs_page.has_next())
        self.assertFalse(clubs_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">', 0)

    def test_successful_empty_search(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs()
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        for club in Club.objects.all():
            self.assertTrue(self._club_is_on_list(club))

    def test_successful_non_empty_search(self):
        self.client.login(email=self.user.email, password="Password123")
        self.form_input['searched'] = "a"
        self._create_test_clubs()
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        for club in Club.objects.filter(name__contains="a"):
            self.assertTrue(self._club_is_on_list(club))

    def test_show_clubs_list_with_pagination_creating_page_not_an_integer_error(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE + 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_incorrect_url = reverse('show_clubs') + '?page=INCORRECTINPUT'
        response = self.client.get(page_incorrect_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going back to the first page
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE)
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_clubs_list_with_pagination_creating_empty_page_error_from_bigger_page_number_than_exists(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE * 2 + 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_big_url = reverse('show_clubs') + '?page=9999'
        response = self.client.get(page_big_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')


    def test_show_clubs_list_with_pagination_creating_empty_page_error_from_smaller_page_number_than_exists(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE * 2 + 1) #creating three pages
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_zero_url = reverse('show_clubs') + '?page=0'
        response = self.client.get(page_zero_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_one_url = reverse('show_clubs') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_negative_url = reverse('show_clubs') + '?page=-999'
        response = self.client.get(page_negative_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_clubs_list_with_pagination_creating_page_not_an_integer_error_after_search(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE + 1)
        self.form_input['searched'] = "NEW_CLUB" # Add search to add to the coverage of the tests
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_incorrect_url = reverse('show_clubs') + '?page=INCORRECTINPUT'
        response = self.client.get(page_incorrect_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going back to the first page
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE)
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_clubs_list_with_pagination_creating_empty_page_error_from_bigger_page_number_than_exists_after_search(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE * 2 + 1)
        self.form_input['searched'] = "NEW_CLUB"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_big_url = reverse('show_clubs') + '?page=9999'
        response = self.client.get(page_big_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def test_get_show_clubs_url_for_asc_sort_by_name(self):
        self.url = reverse('show_clubs', kwargs={'param':'name', 'order': 'asc'})
        self.assertEqual(self.url, '/clubs/name/asc/')

    def test_sort_asc_by_name(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE * 2 + 1)
        self.url = reverse('show_clubs', kwargs={'param':'name', 'order': 'asc'})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_big_url = reverse('show_clubs') + '?page=9999'
        response = self.client.get(page_big_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')


    def test_show_applications_list_with_pagination_creating_empty_page_error_from_smaller_page_number_than_exists_after_search(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE * 2 + 1) #creating three pages
        self.form_input['searched'] = "NEW_CLUB"
        for club in Club.objects.all():
            self.assertTrue(self._club_is_on_list(club))

    def test_get_show_clubs_url_for_des_sort_by_name(self):
        self.url = reverse('show_clubs', kwargs={'param':'name', 'order': 'des'})
        self.assertEqual(self.url, '/clubs/name/des/')

    def test_sort_des_by_name(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_clubs(settings.CLUBS_PER_PAGE * 2 + 1)
        self.url = reverse('show_clubs', kwargs={'param':'name', 'order': 'des'})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_clubs') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_zero_url = reverse('show_clubs') + '?page=0'
        response = self.client.get(page_zero_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_one_url = reverse('show_clubs') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.CLUBS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_negative_url = reverse('show_clubs') + '?page=-999'
        response = self.client.get(page_negative_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')
        for club in Club.objects.all():
            self.assertTrue(self._club_is_on_list(club))

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
