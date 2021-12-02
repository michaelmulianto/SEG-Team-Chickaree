"""unit test for edit club info form"""
from django import forms
from django.test import TestCase
from clubs.forms import EditClubInfoForm
from clubs.models import Club
from django.urls import reverse

class EditClubInfoFormTestCase(TestCase):
    """Unit tests of the edit_club_info form."""

    fixtures = ['clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.url = reverse('edit_account')
        self.form_input = {
            'name' : "Bishops",
            'location': "Paris",
            'description': "The best chess club in France.",
        }
        self.club = Club.objects.get(name="King's Knights")

    def test_form_has_necessary_fields(self):
        form = EditClubInfoForm()
        self.assertIn('name', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('description', form.fields)

    def test_valid_edit_club_info_form(self):
        form = EditClubInfoForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        form = EditClubInfoForm(instance=self.club, data=self.form_input)
        before_count = Club.objects.count()
        form.save()
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(self.club.name, 'Bishops')
        self.assertEqual(self.club.location, 'Paris')
        self.assertEqual(self.club.description, 'The best chess club in France.')
