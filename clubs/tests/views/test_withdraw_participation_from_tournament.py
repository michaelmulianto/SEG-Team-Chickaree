"""Test backend implementation of the application functionality."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Participant, Membership, Tournament
from clubs.tests.helpers import reverse_with_next

class WithdrawParticipationFromTournamentTestCase(TestCase):
    """Test all aspects of withdrawing participation from a tournament"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/default_tournament.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/other_tournaments.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.tournament = Tournament.objects.get(name='Grand Championship')
        self.tournament_with_passed_deadline = Tournament.objects.get(name='Battle 101')
        self.club = Club.objects.get(name="King's Knights")
        self.member = Membership.objects.create(
            user = self.user,
            club = self.club,
            is_officer = False,
            is_owner = False,
        )
        self.participant = Participant.objects.create(
            member = self.member,
            tournament = self.tournament,
        )

        self.url = reverse('withdraw_from_tournament', kwargs = {'tournament_id': self.tournament.id})

    def test_url_of_withdraw_application_to_club(self):
        self.assertEqual(self.url, '/tournament/' + str(self.tournament.id) + '/withdraw/')

    def test_withdraw_from_tournament_redirects_when_not_logged_in(self):
        participant_count_before = Participant.objects.count()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        participant_count_after = Participant.objects.count()
        self.assertEqual(participant_count_after, participant_count_before)

    def test_unsuccessful_withdrawal_when_not_participated(self):
        self.client.login(email=self.user.email, password="Password123")
        Participant.objects.get(tournament=self.tournament, member=self.member).delete()

        participant_count_before = Participant.objects.count()
        response = self.client.post(self.url, follow=True)
        participant_count_after = Participant.objects.count()
        self.assertEqual(participant_count_after, participant_count_before)

        response_url = reverse('show_club', kwargs = {'club_id': self.tournament.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_unsuccessful_withdrawal_after_passed_deadline(self):
        self.client.login(email=self.user.email, password="Password123")
        other_participant = Participant.objects.create(
            member = self.member,
            tournament = self.tournament_with_passed_deadline,
        )
        url = reverse('withdraw_from_tournament', kwargs = {'tournament_id': self.tournament_with_passed_deadline.id})

        participant_count_before = Participant.objects.count()
        response = self.client.post(url, follow=True)
        participant_count_after = Participant.objects.count()
        self.assertEqual(participant_count_after, participant_count_before)

        response_url = reverse('show_club', kwargs = {'club_id': self.tournament.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_successful_withdrawal(self):
        self.client.login(email=self.user.email, password="Password123")
        participant_count_before = Participant.objects.count()
        response = self.client.post(self.url, follow=True)
        participant_count_after = Participant.objects.count()
        self.assertEqual(participant_count_after, participant_count_before-1)

        # Should redirect user somewhere appropriate, indicating success.
        response_url = reverse('show_club', kwargs = {'club_id': self.tournament.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_clubs.html')
