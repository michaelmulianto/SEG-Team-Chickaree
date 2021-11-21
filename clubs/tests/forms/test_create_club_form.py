"""Tests for form used to create a new club"""

from django.test import TestCase
from clubs.models import User
from django import forms
from clubs.forms import CreateClubForm
from django.contrib.auth.hashers import check_password

class CreateClubFormTest(TestCase):
    """Test all aspects of the create club form"""

    def setUp(self):
        self.form_input = {
            'name' : 'x'*10,
            'location' : 'x'*10,
            'description' : 'x'*10
        }

    def test_valid_club_form(self):
        form = CreateClubForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_invalid_club_form_empty_name(self):
        self.form_input['name'] = ''
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_invalid_club_form_location_too_long(self):
        self.form_input['location'] = 'x'*600
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_invalid_club_form_description_too_long(self):
        self.form_input['description'] = 'x'*600
        form = CreateClubForm(data=self.form_input)
        self.assertFalse(form.is_valid())
