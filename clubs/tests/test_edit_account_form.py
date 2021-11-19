from django import forms
from django.test import TestCase
from clubs.forms import EditAccountForm
from clubs.models import User
from django.urls import reverse

class EditAccountFormTestCase(TestCase):
    """Unit tests of the edit_account form."""

    def setUp(self):
        self.url = reverse('edit_account')
        self.form_input = {
            'username' : 'janedoe',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email' : 'janeDoe@example.org',
        }
        self.user = User.objects.create_user(
            '@johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            password = 'Password123',
            is_active=True
        )

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
        user = User.objects.get(username='@johndoe')
        form = EditAccountForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, 'janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janeDoe@example.org')
