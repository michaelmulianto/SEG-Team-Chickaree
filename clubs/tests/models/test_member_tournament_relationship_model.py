"""Tests for base model MemberTournament relationship"""

from django.test import TestCase
from clubs.models import Club, User, Membership, Tournament, MemberTournamentRelationship
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class MemberTournamentRelationshipModelTestCase(TestCase):
    """Tests all aspects of a relationship between a tournament and a member of its club."""
    
    fixtures = ['clubs/tests/fixtures/default_user.json',
            'clubs/tests/fixtures/other_users.json',
            'clubs/tests/fixtures/default_club.json',
            'clubs/tests/fixtures/default_tournament.json',
            'clubs/tests/fixtures/other_tournaments.json']  

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

        self.first_tournament = Tournament.objects.get(name = 'Grand Championship')
        self.second_tournament = Tournament.objects.get(name = 'Just A League')

        self.mtr = MemberTournamentRelationship.objects.create(
            member = self.first_membership,
            tournament = self.first_tournament
        )


    def test_valid_MemeberTournamentRealtionship(self):
        self._assert_MemeberTournamentRealtionship_is_valid()

    #test member
    def test_member_cannot_be_blank(self):
        self.mtr.member = None
        self._assert_MemeberTournamentRealtionship_is_invalid()

    def test_member_must_contain_member_object(self):
        with self.assertRaises(ValueError):
            self.mtr.member = self.club

    def test_deleting_membership_deletes_MemberTournamentRelationship(self):
        self.mtr.member.delete()
        self.assertFalse(MemberTournamentRelationship.objects.filter(member=self.first_membership).exists())

    def test_same_member_can_be_in_various_MemberTournamentRelationships(self):
        newMTR = MemberTournamentRelationship.objects.create(
            member = self.first_membership,
            tournament = self.second_tournament
        )
        self._assert_other_MemeberTournamentRealtionship_is_valid(newMTR)

    
    #test tournament
    def test_tournament_cannot_be_blank(self):
        self.mtr.tournament = None
        self._assert_MemeberTournamentRealtionship_is_invalid()

    def test_tournament_must_contain_member_object(self):
        with self.assertRaises(ValueError):
            self.mtr.tournament = self.club

    def test_deleting_tournament_deletes_MemberTournamentRelationship(self):
        self.mtr.tournament.delete()
        self.assertFalse(MemberTournamentRelationship.objects.filter(tournament=self.first_tournament).exists())

    def test_same_tournament_can_be_in_various_MemberTournamentRelationships(self):
        newMTR = MemberTournamentRelationship.objects.create(
            member = self.second_membership,
            tournament = self.first_tournament
        )
        self._assert_other_MemeberTournamentRealtionship_is_valid(newMTR)


    #test unique constraints
    def test_cannot_have_two_MemberTournamentRelationships_with_same_member_and_tournament(self):
        try:
            MemberTournamentRelationship.objects.create(
                member = self.first_membership,
                tournament = self.first_tournament
            )
        except(IntegrityError):
            self.assertRaises(IntegrityError)


    #Assertions
    def _assert_MemeberTournamentRealtionship_is_valid(self):
        try:
            self.mtr.full_clean()
        except(ValidationError):
            self.fail('Test Member Tournament Relationship should be valid')

    def _assert_MemeberTournamentRealtionship_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.mtr.full_clean() 

    def _assert_other_MemeberTournamentRealtionship_is_valid(self, mtr):
        try:
            mtr.full_clean()
        except(ValidationError):
            self.fail('Test Member Tournament Relationship should be valid')

    def _assert_other_MemeberTournamentRealtionship_is_invalid(self, mtr):
        with self.assertRaises(ValidationError):
            mtr.full_clean()  