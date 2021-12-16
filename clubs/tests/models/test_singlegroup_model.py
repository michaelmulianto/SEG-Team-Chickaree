"""Tests for model of a single group within a group stage."""

from django.test import TestCase
from clubs.models import Participant, Tournament, User, GroupStage, SingleGroup, Match
from django.core.exceptions import ValidationError

class SingleGroupModelTestCase(TestCase):
    """Test all aspects of a single group model."""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json',
    'clubs/tests/fixtures/default_tournament.json',
    'clubs/tests/fixtures/default_tournament_participants.json'
    ]

    # Test setup
    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.tournament = Tournament.objects.get(name = "Grand Championship")
        self.stage = self.tournament.generate_next_round()
        self.group = SingleGroup.objects.filter(group_stage=self.stage)[0]
    
    def test_valid_singlegroup(self):
        self._assert_valid_singlegroup()

    # Test group_stage
    def test_group_stage_cannot_be_blank(self):
        self.group.group_stage= None
        self._assert_invalid_singlegroup()

    def test_group_stage_cannot_contain_non_group_stage_object(self):
        with self.assertRaises(ValueError):
            self.group.group_stage = self.user

    def test_single_group_deletes_when_group_stage_is_deleted(self):
        self.stage.delete()
        self.assertFalse(SingleGroup.objects.filter(id=self.group.id).exists())

    def test_group_stage_does_not_delete_when_single_group_is_deleted(self):
        self.group.delete()
        self.assertTrue(GroupStage.objects.filter(id=self.stage.id).exists())

    # Test winners_required
    def test_winners_required_must_not_be_blank(self):
        self.group.winners_required = None
        self._assert_invalid_singlegroup()

    # Mischallaneous Validation
    def test_one_player_plays_too_many_games_and_one_not_enough(self):
        matches = list(self.group.get_matches())
        match1 = matches[0]
        match2 = matches[1]
        surplus_player = match1.white_player
        
        i = 2
        while (match2.white_player == surplus_player or 
        match2.black_player == surplus_player):
            match2 = matches[i]
            i+=1

        match2.white_player = surplus_player
        match2.save()

        self._assert_invalid_singlegroup()

    
    def test_too_few_matches_assigned_to_group(self):
        self.group.get_matches()[0].delete()
        self._assert_invalid_singlegroup()
        
    def test_get_winners_when_incomplete(self):
        self.assertEqual(self.group.get_winners(), None)

    def test_too_many_matches_assigned_to_group(self):
        participants = list(Participant.objects.filter(tournament=self.tournament))[:2]
        (Match.objects.create(
            white_player = participants[0],
            black_player = participants[1],
            collection = self.group
        )).save()
        
        self._assert_invalid_singlegroup()

    # Assertions
    def _assert_valid_singlegroup(self):
        try:
            self.group.full_clean()
        except (ValidationError):
            self.fail("Test SingleGroup should be valid")

    def _assert_invalid_singlegroup(self):
        with self.assertRaises(ValidationError):
            self.group.full_clean()
