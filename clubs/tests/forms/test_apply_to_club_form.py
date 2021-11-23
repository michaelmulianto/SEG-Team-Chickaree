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
        form = ApplyToClubForm(data=self.input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.input['personalStatement'] = ''
        form = ApplyToClubForm(data=self.input)
        self.assertFalse(form.is_valid())

    def test_form_contains_necessary_fields(self):
        form = ApplyToClubForm()

        # Existence of fields
        self.assertIn('experience', form.fields)
        self.assertIn('personalStatement', form.fields)

        # Correct field for experience
        exp_field = form.fields['experience']
        self.assertTrue(isinstance(exp_field, forms.ChoiceField))