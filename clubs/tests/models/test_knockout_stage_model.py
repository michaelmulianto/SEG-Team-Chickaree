"""Tests for single group model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Match, Participant, Tournament, Club, User, Membership, GroupStage, SingleGroup,  KnockoutStage
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class KnockOutStageModelTestCase(TestCase):
    """Test all aspects of a single group model."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_clubs.json',
                'clubs/tests/fixtures/default_tournament.json',
                'clubs/tests/fixtures/other_tournaments.json'
                ]

    def setUp(self):
        
        self.knockoutStage = KnockoutStage.objects.create(
            tournament = self.tournament, # from TournamentStageBase which inherits RoundOfMatches
            round_num = 1, # from TournamentStageBase
        )



    
    # Assertions
    def _assert_valid_knockout_stage(self):
        try:
            self.knockoutStage.full_clean()
        except (ValidationError):
            self.fail("Test KnockoutStage should be valid")

    def _assert_invalid_knockout_stage(self):
        with self.assertRaises(ValidationError):
            self.knockoutStage.full_clean()
