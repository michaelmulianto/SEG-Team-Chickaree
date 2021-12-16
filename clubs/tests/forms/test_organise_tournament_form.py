"""Tests for form used to create a new account"""

from django.test import TestCase
from clubs.models import Tournament, Club
from django import forms
from clubs.forms import OrganiseTournamentForm

class OrganiseTournamentFormTestCase(TestCase):
    """Test all aspects of the organise tournament form"""

    fixtures = ['clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.form_input = {
          'name' : "Grand Championship",
          'description' : "The most prestigious tournament in London.",
          'capacity' : 16,
          'deadline' : "2022-01-14T00:00:00+00:00",
          'start' : "2022-01-16T00:00:00+00:00",
          'end' : "2022-01-20T00:00:00+00:00"
        }
        self.club = Club.objects.get(name="King's Knights")

    def test_valid_organise_tournament_form(self):
        form = OrganiseTournamentForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_contains_necessary_fields(self):
        form = OrganiseTournamentForm()

        # Existence of fields
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('capacity', form.fields)
        self.assertIn('deadline', form.fields)
        self.assertIn('start', form.fields)
        self.assertIn('end', form.fields)

        deadline_field = form.fields['deadline']
        self.assertTrue(isinstance(deadline_field, forms.DateTimeField))

        start_field = form.fields['start']
        self.assertTrue(isinstance(start_field, forms.DateTimeField))

        end_field = form.fields['end']
        self.assertTrue(isinstance(end_field, forms.DateTimeField))

    def test_form_uses_model_validation(self):
        self.form_input['capacity'] = 17
        form = OrganiseTournamentForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_saves_correctly(self):
        before_count = Tournament.objects.count()
        form = OrganiseTournamentForm(data=self.form_input)
        form.save(self.club)
        after_count = Tournament.objects.count()
        self.assertEqual(after_count, before_count+1)
        tournament = Tournament.objects.get(name='Grand Championship')
        self.assertEqual(tournament.capacity, 16)
