"""Tests for the edit_club_info view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import EditClubInfoForm
from clubs.models import Club, User
from clubs.tests.helpers import reverse_with_next

class EditClubInfoViewTest(TestCase):
    """Test suite for the edit_club_info view."""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_clubs.json',
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.form_input = {
            'name' : "Bishops",
            'location': "Paris",
            'description': "The best chess club in France.",
        }
        self.club = Club.objects.get(name="King's Knights")
        self.second_club = Club.objects.get(name="Queen's Rooks")
        self.user = User.objects.get(username='johndoe')

        self.url = reverse('edit_club_info', kwargs = {'club_id': self.club.id})

    def test_edit_club_info_url(self):
        self.assertEqual(self.url, '/club/' + str(self.club.id) + '/edit')

    def test_get_edit_club_info(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubInfoForm))
        self.assertEqual(form.instance, self.club)

    def test_get_edit_club_info_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_unsuccesful_edit_club_info_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['name'] = 'A' * 51
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubInfoForm))
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "King's Knights")
        self.assertEqual(self.club.location, "King's College London")
        self.assertEqual(self.club.description, "The best chess club in London.")

    def test_unsuccessful_edit_club_info_due_to_duplicate_name(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['name'] = self.second_club.name
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club_info.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditClubInfoForm))
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "King's Knights")
        self.assertEqual(self.club.location, "King's College London")
        self.assertEqual(self.club.description, "The best chess club in London.")

    def test_succesful_edit_account_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('show_clubs')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "Bishops")
        self.assertEqual(self.club.location, "Paris")
        self.assertEqual(self.club.description, "The best chess club in France.")
