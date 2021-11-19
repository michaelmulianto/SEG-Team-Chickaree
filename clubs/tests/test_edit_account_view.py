"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import EditAccountForm
from clubs.models import User

class EditAccountViewTest(TestCase):
    """Test suite for the profile view."""

    def setUp(self):
        self.url = reverse('edit_account')
        self.form_input = {
            'username' : 'johndoeeee',
            'first_name': 'Johnnnn',
            'last_name': 'Doeeee',
            'email' : 'johndoe2@example.org',
        }
        self.user = User.objects.create_user(
            '@johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            password = 'Password123',
            is_active=True
        )

    def test_edit_account_url(self):
        self.assertEqual(self.url, '/edit_account/')

    def test_get_edit_user(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertEqual(form.instance, self.user)

    def test_unsuccesful_edit_account_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['first_name'] = 'B' * 50
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_unsuccessful_edit_account_update_due_to_duplicate_username(self):
        self.client.login(username=self.user.username, password='Password123')
        second_user = self._create_second_user()
        self.form_input['username'] = second_user.username
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_unsuccessful_edit_account_update_due_to_duplicate_email(self):
        self.client.login(username=self.user.username, password='Password123')
        second_user = self._create_second_user()
        self.form_input['email'] = second_user.email
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_account.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditAccountForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, '@johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')

    def test_succesful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('account')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'account.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoeeee')
        self.assertEqual(self.user.first_name, 'Johnnnn')
        self.assertEqual(self.user.last_name, 'Doeeee')
        self.assertEqual(self.user.email, 'johndoe2@example.org')


    def _create_second_user(self):
        second_user = User.objects.create_user(
                    '@janedoe',
                    first_name = 'Jane',
                    last_name = 'Doe',
                    email = 'janedoe@example.org',
                    password = 'Password123',
                    is_active=True
        )

        return second_user
