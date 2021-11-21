"""
Tests for form used to apply to a club.

It should be noted that saving Application objects is handled in the view.
"""

from django.test import TestCase
from clubs.models import Application
from django import forms
from clubs.forms import ApplyToClubForm

class ApplyToClubFormTestCase(TestCase):
    """Test all aspects of the apply to club form"""

    def setUp(self):
        self.input = {
            'experience' : 1,
            'personalStatement' : 'I love chess!',
        }

    def test_valid_apply_to_club_form(self):
        form = CreateClubForm(data=self.input)
        self.assertTrue(form.is_valid())

    def test_invalid_create_club_form(self):
        self.input['personalStatement'] = ''
        form = CreateClubForm(data=input)
        self.assertFalse(form.is_valid())