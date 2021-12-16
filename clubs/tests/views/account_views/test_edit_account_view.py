"""Tests for the edit_account view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import EditAccountForm
from clubs.models import User
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin

class EditAccountViewTest(TestCase, MenuTesterMixin):
    """Test suite for the edit_account view."""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('edit_account')
        self.form_input = {
            'username' : 'johndoeeee',
            'first_name': 'Johnnnn',
            'last_name': 'Doeeee',
            'email' : 'johndoe2@example.org',
        }
        self.user = User.objects.get(username='johndoe')
        self.second_user = User.objects.get(username='janedoe')

    def test_edit_account_url(self):
        self.assertEqual(self.url, '/account/edit/')

    def test_get_edit_account(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertEqual(form.instance, self.user)
        self.assert_menu(response)

    def test_get_edit_account_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        response_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    def test_unsuccesful_edit_account_update(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['first_name'] = 'B' * 50
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_unsuccessful_edit_account_update_due_to_duplicate_username(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['username'] = self.second_user.username
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_unsuccessful_edit_account_update_due_to_duplicate_email(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = self.second_user.email
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_succesful_edit_account_update(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('account')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'account/account.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoeeee')
        self.assertEqual(self.user.first_name, 'Johnnnn')
        self.assertEqual(self.user.last_name, 'Doeeee')
        self.assertEqual(self.user.email, 'johndoe2@example.org')
