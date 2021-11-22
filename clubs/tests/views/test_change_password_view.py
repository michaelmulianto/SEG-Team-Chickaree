"""Test user-facing implementation of the sign up form."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User
from clubs.forms import SignUpForm
from django.contrib.auth.hashers import check_password
from clubs.tests.helpers import LogInTester

class ChangePasswordViewTestCase(TestCase, LogInTester):
    pass
