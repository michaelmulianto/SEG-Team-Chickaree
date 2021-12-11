from django.test import TestCase
from clubs.models import KnockoutStage, Club, Match, StageInterface, User, Membership, Participant, Tournament
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

        # self.stage = StageInterface.objects.create(
        #     tournament = self.tournament,
        #     round_num = 1
        # )

        # self.knockoutStage = KnockoutStage.objects.create( 
        #     tournament = self.tournament,
        #     round_num = 1
        # )

        self.match = Match.objects.create(
            white_player = self.first_par,
            black_player = self.second_par,
            stage = KnockoutStage.objects.create(
                tournament = self.tournament,
                round_num = 1
            ),
            result = 1 # white player wins
        )



    def test_assert_number_of_matches_must_be_a_power_of_two(self):
        pass

    def test_assert_each_player_must_only_play_one_match(self):
        pass

    def test_white_player_wins_the_match_shows_correctly(self):
        pass

    def test_white_player_wins_the_match_shows_correctly(self):
        pass

    def test_we_can_access_tournament_from_superclass(self):
        pass

    def test_we_can_access_round_num_from_superclass(self):
        pass


    def _assert_knockout_stage_is_valid(self):
        try:
            self.knockoutStage.full_clean()
        except(ValidationError):
            self.fail("Test knockoutStage should be valid")

    def _assert_knockout_stage_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.knockoutStage.full_clean()