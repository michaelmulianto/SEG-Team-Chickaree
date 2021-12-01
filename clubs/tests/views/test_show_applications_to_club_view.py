"""Test backend implementation of the application viewer functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member, Application
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from with_asserts.mixin import AssertHTMLMixin

class ShowApplicationsToClubTestCase(TestCase, MenuTesterMixin):
    """Test all aspects of the show applications to club view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/second_user.json',
    ]
    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.membership = Member.objects.create(
            club = self.club,
            user = self.user,
            is_owner = True
        )

        self.url = reverse('show_applications_to_club', kwargs = {'club_id': self.club.id})

    def test_url_of_show_applications_to_club(self):
        self.assertEqual(self.url, '/club/' + str(self.club.id) + '/applications')

    def test_show_application_to_club_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_application_to_club_redirects_when_not_owner_of_club(self):
        self.membership.is_owner = False
        self.membership.save(update_fields=['is_owner'])

        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)

        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_show_application_to_club_redirects_when_invalid_club_id_entered(self):
        self.url = reverse('show_applications_to_club', kwargs = {'club_id': 0})
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_successful_show_applications_to_club(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_list.html')
        self.assert_menu(response)

    def test_template_does_not_show_header_fields_when_there_are_no_aplications(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)

        with self.assertHTML(response) as html:
            noTableTextContainer = html.find('body/div/div/div/table/tr/p')
            self.assertEqual(noTableTextContainer.text, ' No more applications ')

    def test_template_shows_header_fields_when_there_is_at_least_one_aplication(self):
        second_user = User.objects.get(username='janedoe')
        Application.objects.create(
            club = self.club,
            user = second_user,
            personal_statement = 'I love chess!'
        )


        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        with self.assertHTML(response) as html:
            TableTextContainer = html.find('body/div/div/div/table/table/tr/th')
            self.assertEqual(TableTextContainer.text, 'Name')

    def test_template_shows_header_fields_when_there_are_more_than_one_aplicationa(self):
        second_user = User.objects.get(username='janedoe')
        Application.objects.create(
            club = self.club,
            user = second_user,
            personal_statement = 'I love chess!'
        )

        third_user = User.objects.get(username='mariadandy')
        Application.objects.create(
            club = self.club,
            user = third_user,
            personal_statement = "Cool club you've got there"
        )


        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        with self.assertHTML(response) as html:
            TableTextContainer = html.find('body/div/div/div/table/table/tr/th')
            self.assertEqual(TableTextContainer.text, 'Name')
