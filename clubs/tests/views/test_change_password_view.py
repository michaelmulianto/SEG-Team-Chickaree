"""
Test backend implementation of password changing.

Note: a built in password change form is being used, hence the lack of tests specific to the front end.
"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.forms import SignUpForm
from django.contrib.auth.hashers import check_password
from clubs.tests.helpers import LogInTester

class ChangePasswordViewTestCase(TestCase, LogInTester):
    """Test all aspects of change password view."""
    fixtures = [
        'clubs/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username="johndoe")
