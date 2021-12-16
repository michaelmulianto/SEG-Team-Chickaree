"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Membership
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.conf import settings

class MembersTestCase(TestCase, MenuTesterMixin):
    """Test aspects of account view"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member = Membership.objects.create(
            user = self.user,
            club = self.club,
            is_officer = False,
            is_owner = False,
        )
        self.url = reverse('members_list', kwargs={'club_id': self.club.id})

    def test_members_list_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/members/')

    def test_get_user_list_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_members_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)

    def test_get_applications_to_my_clubs_for_applications_with_pagination(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_memberships_for_default_club(settings.MEMBERSHIPS_PER_PAGE*2+3 -1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE)
        memberships_page = response.context['page_obj']
        self.assertFalse(memberships_page.has_previous())
        self.assertTrue(memberships_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_one_url = reverse('members_list', kwargs={'club_id': self.club.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE)
        memberships_page = response.context['page_obj']
        self.assertFalse(memberships_page.has_previous())
        self.assertTrue(memberships_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_two_url = reverse('members_list', kwargs={'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE)
        memberships_page = response.context['page_obj']
        self.assertTrue(memberships_page.has_previous())
        self.assertTrue(memberships_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_three_url = reverse('members_list', kwargs={'club_id': self.club.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 3)
        memberships_page = response.context['page_obj']
        self.assertTrue(memberships_page.has_previous())
        self.assertFalse(memberships_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_members_list_with_pagination_does_not_contain_page_traversers_if_not_enough_members(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_memberships_for_default_club(settings.MEMBERSHIPS_PER_PAGE-2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        memberships_page = response.context['page_obj']
        self.assertFalse(memberships_page.has_previous())
        self.assertFalse(memberships_page.has_next())
        self.assertFalse(memberships_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">', 0)

    def test_show_members_list_with_pagination_creating_page_not_an_integer_error(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_memberships_for_default_club(settings.MEMBERSHIPS_PER_PAGE + 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_incorrect_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=INCORRECTINPUT'
        response = self.client.get(page_incorrect_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        #test we're going back to the first page
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE)
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_members_list_with_pagination_creating_empty_page_error_from_bigger_page_number_than_exists(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_memberships_for_default_club(settings.MEMBERSHIPS_PER_PAGE * 2 + 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_big_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=9999'
        response = self.client.get(page_big_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')


    def test_show_members_list_with_pagination_creating_empty_page_error_from_smaller_page_number_than_exists(self):
        self.client.login(email=self.user.email, password="Password123")
        self._create_test_memberships_for_default_club(settings.MEMBERSHIPS_PER_PAGE * 2 + 1) #creating three pages
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_zero_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=0'
        response = self.client.get(page_zero_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_one_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.MEMBERSHIPS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_negative_url = reverse('members_list', kwargs = {'club_id': self.club.id}) + '?page=-999'
        response = self.client.get(page_negative_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/members_list.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def _create_test_memberships_for_default_club(self, members_count = 10):
        for future_member in range(members_count):
            
            user = User.objects.create(
                username = f'USERNAME{future_member}',
                last_name = f'LASTNAME{future_member}',
                first_name = f'FIRSTNAME{future_member}',
                email = f'EMAIL{future_member}@gmail.com',
                bio = f'BIO{future_member}',
                experience = 1
            )

            Membership.objects.create(
                user = user,
                club = self.club
            )

    def _create_test_users(self, user_count=10):
        users = []
        for user_id in range(user_count):
            new_user = User.objects.create_user(
                f'@user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
            )
            users.append(new_user)
            Membership.objects.create(
                user = users,
                club = self.club,
                is_officer = False,
                is_owner = False,
            )
