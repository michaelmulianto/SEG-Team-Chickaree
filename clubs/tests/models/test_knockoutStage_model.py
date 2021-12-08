from django.test import TestCase
from clubs.models import KnockoutStage, Club, Match, StageInterface, User, Membership, Participant, Tournament
from django.core.exceptions import ValidationError

class KnockoutStageModelTestCase(TestCase):
    """Test all aspects of a knockout stage"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
                'clubs/tests/fixtures/other_users.json',
                'clubs/tests/fixtures/default_club.json',
                'clubs/tests/fixtures/other_clubs.json', 
                'clubs/tests/fixtures/other_tournaments.json']   

    def setUp(self):
        self.club = Club.objects.get(name = "King\'s Knights")

        self.first_user = User.objects.get(username = "johndoe")
        self.second_user = User.objects.get(username = "janedoe")
        # self.third_user = User.objects.get(username = "richarddoe")
        # self.fourth_user = User.objects.get(username = "mariadandy")

        self.first_membership = Membership.objects.create(
            user = self.first_user,
            club = self.club
        )
        self.second_membership = Membership.objects.create(
            user = self.second_user,
            club = self.club
        )
        # self.third_membership = Membership.objects.create(
        #     user = self.third_user,
        #     club = self.club
        # )
        # self.fourth_membership = Membership.objects.create(
        #     user = self.fourth_user,
        #     club = self.club
        # )


        self.tournament = StageInterface.objects.create(
            tournament = Tournament.objects.get(name = "Just A League"),
            round_num = 1
        )


        self.first_par = Participant.objects.create(
            round_eliminated = 1,
            member = self.membership,
            tournament = self.tournament
        )
        self.second_par = Participant.objects.create(
            round_eliminated = 1,
            member = self.membership,
            tournament = self.tournament
        )
        # self.third_par = Participant.objects.create(
        #     round_eliminated = 2,
        #     member = self.membership,
        #     tournament = self.tournament
        # )
        # self.fourth_par = Participant.objects.create(
        #     round_eliminated = 1,
        #     member = self.membership,
        #     tournament = self.tournament
        # )


        self.match = Match.objects.create(
            white_player = self.first_par,
            black_player = self.second_par,
            stage = self.stage,
            result = 1,
        )

        # self.second_match = Match.objects.create(
        #     white_player = self.first_par,
        #     black_player = self.second_par,
        #     stage = self.stage,
        #     result = 1,
        # )

        self.knockoutRoung = KnockoutStage.objects.create()



    def _assert_knockout_stage_is_valid(self):
        try:
            self.