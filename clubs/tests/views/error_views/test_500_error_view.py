"""Unit test for the 500 error page view"""
from django.http import request
from django.shortcuts import render
from django.test import TestCase, override_settings
from clubs.models import User
from clubs.tests.helpers import MenuTesterMixin
from clubs.views.errors import server_error_custom
from django.template.loader import get_template

class Http500ErrorViewTestCase(TestCase, MenuTesterMixin):

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')


    @override_settings(DEBUG=False)
    def test_force_500_error(self):
        self.client.login(email=self.user.email, password='Password123')
        response = server_error_custom(request)
        self.assertEqual(response.status_code, 500)
        created_response = render(request, 'http500ErrorPage.html')
        created_response.status_code = 500
        self.assertEqual(response.headers, created_response.headers)
        self.assertEqual(response.headers['Content-Type'], created_response.headers['Content-Type'])

    @override_settings(DEBUG=False)
    def test_force_500_error_when_not_logged_in(self):
        response = server_error_custom(request)
        self.assertEqual(response.status_code, 500)
        created_response = render(request, 'http500ErrorPage.html')
        created_response.status_code = 500
        self.assertEqual(response.headers, created_response.headers)
        self.assertEqual(response.headers['Content-Type'], created_response.headers['Content-Type'])
