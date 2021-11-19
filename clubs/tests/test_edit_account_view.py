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
            'first_name': 'John2',
            'last_name': 'Doe2',
            'username' : 'johndoe2',
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

    def test_unsuccesful_profile_update(self):
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
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')
