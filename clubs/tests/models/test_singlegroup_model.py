"""Tests for single group model, found in clubs/models.py"""

from django.test import TestCase
from clubs.models import Match, Participant, Tournament, Club, User, Membership, GroupStage, SingleGroup
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class SingleGroupModelTestCase(TestCase):
    """Test all aspects of a single group model."""

    fixtures = ['clubs/tests/fixtures/default_user.json','clubs/tests/fixtures/other_users.json','clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/other_clubs.json', 'clubs/tests/fixtures/other_tournaments.json', 'clubs/tests/fixtures/default_tournament.json']

    # Test setup
    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.GroupStage = GroupStage.objects.create(
            tournament = Tournament.objects.get(name = "Grand Championship"),
            round_num = 1
        )
        self.SingleGroup = SingleGroup.objects.create(
            group_stage = self.GroupStage,
            winners_required = 1
        )
    
    # def test_valid_singlegroup(self):
    #     self._assert_valid_singlegroup()

    # Test group_stage
    def test_group_stage_cannot_be_blank(self):
        self.SingleGroup.group_stage= None
        self._assert_invalid_singlegroup()

    def test_group_stage_cannot_contain_non_group_stage_object(self):
        with self.assertRaises(ValueError):
            self.SingleGroup.group_stage = self.user

    def test_single_group_deletes_when_group_stage_is_deleted(self):
        self.GroupStage.delete()
        self.assertFalse(SingleGroup.objects.filter(group_stage=self.SingleGroup.group_stage).exists())

    def test_group_stage_does_not_delete_when_single_group_is_deleted(self):
        self.SingleGroup.delete()
        self.assertTrue(GroupStage.objects.filter(tournament = self.GroupStage.tournament).exists())

    # Test winners_required
    def test_winners_required_must_not_be_blank(self):
        self.SingleGroup.winners_required = None
        with self.assertRaises(ValidationError):
            self.SingleGroup.full_clean()

    # Assertions
    def _assert_valid_singlegroup(self):
        try:
            self.SingleGroup.full_clean()
        except (ValidationError):
            self.fail("Test SingleGroup should be valid")

    def _assert_invalid_singlegroup(self):
        with self.assertRaises(ValidationError):
            self.SingleGroup.full_clean()
