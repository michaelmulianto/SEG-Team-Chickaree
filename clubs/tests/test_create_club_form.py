"""Tests for form used to create a new club"""

from django.test import TestCase
from clubs.models import User
from django import forms
from clubs.forms import CreateClubForm
from django.contrib.auth.hashers import check_password

class CreateClubFormTest(TestCase):
    """Test all aspects of the create club form"""

    def test_valid_create_club_form(self):
        input = {
            'name' : 'x'*10,
            'location' : 'x'*10,
            'description' : 'x'*10
        }
        form = CreateClubForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_create_club_form(self):
        input = {
            'name' : '',
            'location' : 'x'*600,
            'description' : 'x'*600
        }
        form = CreateClubForm(data=input)
        self.assertFalse(form.is_valid())
