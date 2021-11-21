"""Unit test for the log in view"""

from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from clubs.forms import LogInForm
from clubs.models import User
from clubs.tests.helpers import LogInTester

class LogInViewTestCase(TestCase, LogInTester):
    """Test all aspects of log in view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_in')
        self.form_input = {
            'username': 'johndoe',
            'password': 'Password123'
        }
        self.user = User.objects.get(username='johndoe')

    def test_get_log_in_url(self):
        self.assertEqual('/log_in/', self.url)

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_log_in_with_blank_username(self):
        self.form_input['username'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        self.form_input['password'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_unsuccessful_log_in(self):
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_successful_log_in(self):
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('account')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'account.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)


    def test_valid_log_in_by_inacitve_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
