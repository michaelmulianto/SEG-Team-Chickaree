"""Test backend of the create club form."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership, Participant, Tournament, Organiser
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin


class JoinTournamentViewTest(TestCase, MenuTesterMixin):
    """Test all aspects of the join tournament view"""

    fixtures = ['clubs/tests/fixtures/default_tournament_participants.json','clubs/tests/fixtures/default_user.json', 'clubs/tests/fixtures/other_users.json', 'clubs/tests/fixtures/other_clubs.json', 'clubs/tests/fixtures/default_tournament.json', 'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(username = 'johndoe')
        self.club = Club.objects.get(name = "King's Knights")
        self.tournament = Tournament.objects.get(name = 'Grand Championship')
        self.member = Membership.objects.create(
            user = self.user,
            club = self.club,
        )
        self.member_two = Membership.objects.create(
            user = User.objects.get(username = 'janedoe'),
            club = self.club,
            is_owner = True
        )

        self.url = reverse('join_tournament', kwargs={'tournament_id': self.tournament.id})

    def test_join_tournament_url(self):
        self.assertEqual(self.url, f'/club/{self.tournament.id}/join_tournament/')

    def test_get_join_tournament_redirects_when_not_logged_in(self):
        response = self.client.post(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_join_tournament(self):
        self.client.login(email=self.user.email, password="Password123")

        # We need to test that participant has been created
        participant_count_before = Participant.objects.count()
        response = self.client.get(self.url, follow=True)
        participant_count_after = Participant.objects.count()

        self.assertEqual(participant_count_after, participant_count_before+1)


    def test_tournament_is_full(self):
        self.client.login(email=self.user.email, password='Password123')

        Participant.objects.create(
            member = self.member_two,
            tournament = self.tournament
        )

        participant_count_before = Participant.objects.count()
        response = self.client.get(self.url, follow=True)
        participant_count_after = Participant.objects.count()

        self.assertEqual(participant_count_after, participant_count_before)

        redirect_url = reverse('show_club', kwargs = {'club_id': self.tournament.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_is_not_member(self):
        self.client.login(email=self.user.email, password='Password123')

        self.member.delete()
        participant_count_before = Participant.objects.count()
        response = self.client.get(self.url, follow=True)
        participant_count_after = Participant.objects.count()

        self.assertEqual(participant_count_after, participant_count_before)

    def test_user_is_organiser(self):
        self.client.login(email=self.user.email, password='Password123')

        Organiser.objects.create(
            member = self.member,
            tournament = self.tournament
        )

        participant_count_before = Participant.objects.count()
        response = self.client.get(self.url, follow=True)
        participant_count_after = Participant.objects.count()

        self.assertEqual(participant_count_after, participant_count_before)

        redirect_url = reverse('show_club', kwargs = {'club_id': self.tournament.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_is_already_in_tournament(self):
        self.client.login(email=self.user.email, password='Password123')

        Participant.objects.create(
            member = self.member,
            tournament = self.tournament
        )

        participant_count_before = Participant.objects.count()
        response = self.client.get(self.url, follow=True)
        participant_count_after = Participant.objects.count()

        self.assertEqual(participant_count_after, participant_count_before)

        redirect_url = reverse('show_club', kwargs = {'club_id': self.tournament.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
