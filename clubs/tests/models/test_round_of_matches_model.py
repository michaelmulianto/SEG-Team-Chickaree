"""
Tests for generic round of matches.
"""

from django.test import TestCase
from clubs.models import RoundOfMatches, Tournament
from django.core.exceptions import ValidationError

class RoundOfMatchesModelTestCase(TestCase):
    """Test all aspects of a generic Round of Matches."""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_tournament.json'
        ]

    # Test setup
    def setUp(self):
        self.tourn = Tournament.objects.get(id=1)
        self.round = RoundOfMatches.objects.create(tournament=self.tourn)


    def test_valid_roundofmatches_object(self):
        self._assert_round_is_valid()
    
    def test_tournament_not_unique(self):
        RoundOfMatches.objects.create(tournament=self.tourn)
        self._assert_round_is_valid()
        
    def test_tournament_must_be_type_Tournament(self):
        with self.assertRaises(ValueError):
            self.round.tournament = "WRONG INPUT"
    

    #assertions
    def _assert_round_is_valid(self):
        try:
            self.round.full_clean()
        except (ValidationError):
            self.fail("Test round should be valid")

    def _assert_round_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.round.full_clean()
