"""unit test for edit account form"""
from django import forms
from django.test import TestCase
from clubs.forms import EditAccountForm
from clubs.models import User
from django.urls import reverse

class EditAccountFormTestCase(TestCase):
    """Unit tests of the edit_account form."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('edit_account')
        self.form_input = {
            'username' : 'janedoe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email' : 'janedoe@example.org',
        }
        self.user = User.objects.get(username='johndoe')

    def test_form_has_necessary_fields(self):
        form = EditAccountForm()
        self.assertIn('username', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

    def test_valid_edit_account_form(self):
        form = EditAccountForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'b' * 33
        form = EditAccountForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = EditAccountForm(instance=self.user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(self.user.username, 'janedoe')
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'janedoe@example.org')
