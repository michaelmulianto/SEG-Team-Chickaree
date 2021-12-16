"""Test backend implementation of the sign up form."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.conf import settings
from clubs.models import User
from clubs.forms import SignUpForm
from clubs.tests.helpers import LogInTester, MenuTesterMixin


class SignUpViewTestCase(TestCase, LogInTester, MenuTesterMixin):
    """Test all aspects of the sign up view."""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.org',
            'bio': 'hi',
            'experience': 2,
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'account/sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)
        self.assert_no_menu(response)

    def test_get_sign_up_redirects_when_logged_in(self):
        self.client.login(email='johndoe@example.org', password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')

    def test_unsuccessful_sign_up(self):
        before_count = User.objects.count()
        self.form_input['username'] = 'bad username'
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, 'account/sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response_url = reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertRedirects(response, response_url, status_code=302,
        target_status_code=200) #REDIRECT
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        user = User.objects.get(username='janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())
