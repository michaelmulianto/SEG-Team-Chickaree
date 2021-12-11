from django.test import TestCase
from clubs.models import KnockoutStage, Club, Match, StageInterface, User, Membership, Participant, Tournament, GroupStage, SingleGroup
from django.core.exceptions import ValidationError

class KnockoutStageModelTestCase(TestCase):
    """Test all aspects of a knockout stage"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/default_tournament.json'
                ]   

    def setUp(self):
        self.club = Club.objects.get(name = "King\'s Knights")

        self.first_user = User.objects.get(username = "johndoe")
        self.second_user = User.objects.get(username = "janedoe")

        self.first_membership = Membership.objects.create(
            user = self.first_user,
            club = self.club
        )
        self.second_membership = Membership.objects.create(
            user = self.second_user,
            club = self.club
        )

        self.tournament = Tournament.objects.get(name = "Grand Championship")

        self.first_par = Participant.objects.create(
            member = self.first_membership,
            tournament = self.tournament
        )
        self.second_par = Participant.objects.create(
            member = self.second_membership,
            tournament = self.tournament
        )

        self.groupStage = GroupStage.objects.create( 
            tournament = self.tournament,
            round_num = 1
        )

        self.match = Match.objects.create(
            white_player = self.first_par,
            black_player = self.second_par,
            stage = self.knockoutStage,
            result = 1 # white player wins
        )


    def test_valid_groupStage(self):
        self._assert_group_stage_is_valid()

    def test_group_stage_must_have_at_least_one_single_group_assignmed_to_it(self):
        pass

    def test_group_stage_cannot_be_blank(self):
        self.groundStage = None
        self._assert_group_stage_is_invalid

    def test_get_winners_resturns_participant_object(self):
        pass

    def _assert_group_stage_is_valid(self):
        try:
            self.groupStage.full_clean()
        except(ValidationError):
            self.fail("Test groupStage should be valid")

    def _assert_group_stage_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.groupStage.full_clean()