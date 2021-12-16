"""Test backend implementation of the application viewer functionality."""

from django.template import RequestContext
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership, Application
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from with_asserts.mixin import AssertHTMLMixin
from django.conf import settings
from django.template.loader import render_to_string

class ShowApplicationsToClubTestCase(TestCase, MenuTesterMixin):
    """Test all aspects of the show applications to club view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_users.json',
    ]
    def setUp(self):
        self.user_owner = User.objects.get(username='johndoe')
        self.user_officer = User.objects.get(username='janedoe')
        self.user_applicant = User.objects.get(username='richarddoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member_club_owner = Membership.objects.create(
            club = self.club,
            user = self.user_owner,
            is_owner = True
        )
        self.member_club_owner = Membership.objects.create(
            club = self.club,
            user = self.user_officer,
            is_officer = True
        )
        self.application = Application.objects.create(
            club = self.club,
            user = self.user_applicant,
            personal_statement = 'I love chess!'
        )

        self.url = reverse('show_applications_to_club', kwargs = {'club_id': self.club.id})

    def test_url_of_show_applications_to_club(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/applications/')

    def test_show_application_to_club_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_application_to_club_redirects_when_not_owner_of_club(self):
        self.client.login(email=self.user_applicant.email, password="Password123")
        response = self.client.get(self.url, follow=True)

        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_club.html')

    def test_show_application_to_club_redirects_when_invalid_club_id_entered(self):
        self.url = reverse('show_applications_to_club', kwargs = {'club_id': 0})
        self.client.login(email=self.user_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')

    def test_successful_show_applications_to_club_officer(self):
        self.client.login(email=self.user_officer.email, password="Password123")
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/application_list.html')
        self.assert_menu(response)

    def test_successful_show_applications_to_club_owner(self):
        self.client.login(email=self.user_owner.email, password="Password123")
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/application_list.html')
        self.assert_menu(response)

    def test_template_does_not_show_header_fields_when_there_are_no_aplications(self):
        self.client.login(email=self.user_owner.email, password="Password123")
        self.application.delete()
        self.assertTrue(not Application.objects.filter(club=self.club).exists())
        response = self.client.get(self.url)

        with self.assertHTML(response) as html:
            noTableTextContainer = html.find('body/div/div/div/table/tr/td/b')
            self.assertEqual(noTableTextContainer.text, 'No more applications')

    def test_template_shows_header_fields_when_there_is_at_least_one_aplication(self):
        second_user = User.objects.get(username='janedoe')


        self.client.login(email=self.user_owner.email, password="Password123")
        response = self.client.get(self.url)
        with self.assertHTML(response) as html:
            TableTextContainer = html.find('body/div/div/div/table/tr/th')
            self.assertEqual(TableTextContainer.text, None)

    def test_template_shows_header_fields_when_there_are_more_than_one_aplicationa(self):

        user_applicant2 = User.objects.get(username='mariadandy')
        Application.objects.create(
            club = self.club,
            user = user_applicant2,
            personal_statement = "Cool club you've got there"
        )

        self.client.login(email=self.user_owner.email, password="Password123")
        response = self.client.get(self.url)
        with self.assertHTML(response) as html:
            TableTextContainer = html.find('body/div/div/div/table/tr/th')
            self.assertEqual(TableTextContainer.text, None)

    def test_get_applications_to_my_clubs_for_applications_with_pagination(self):
        self.client.login(email=self.user_owner.email, password="Password123")
        self._create_test_applications_for_default_club(settings.APPLICATIONS_PER_PAGE*2+3-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/application_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.APPLICATIONS_PER_PAGE)
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_one_url = reverse('show_applications_to_club', kwargs = {'club_id': self.club.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/application_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.APPLICATIONS_PER_PAGE)
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_two_url = reverse('show_applications_to_club', kwargs = {'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/application_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.APPLICATIONS_PER_PAGE)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_three_url = reverse('show_applications_to_club', kwargs = {'club_id': self.club.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/application_list.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 3)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_applications_list_with_pagination_does_not_contain_page_traversers_if_not_enough_applications(self):
        self.client.login(email=self.user_owner.email, password="Password123")
        self._create_test_applications_for_default_club(settings.APPLICATIONS_PER_PAGE-2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club/application_list.html')
        self.assert_menu(response)
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertFalse(applications_page.has_other_pages())
        self.assertContains(response, "class='pagination'", 0)

    def _create_test_applications_for_default_club(self, banned_members_count = 10):
        for future_applicant in range(banned_members_count):
            
            user = User.objects.create(
                username = f'USERNAME{future_applicant}',
                last_name = f'LASTNAME{future_applicant}',
                first_name = f'FIRSTNAME{future_applicant}',
                email = f'EMAIL{future_applicant}@gmail.com',
                bio = f'BIO{future_applicant}',
                experience = 1
            )

            Application.objects.create(
                club = self.club,
                user = user,
                personal_statement = "PERSONAL STATEMENT"
            )