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

    
