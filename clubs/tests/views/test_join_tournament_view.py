"""Test backend of the create club form."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership, Participant
from clubs.forms import CreateClubForm
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin


class JoinTournamentViewTest(TestCase, MenuTesterMixin):
    """Test all aspects of the create club view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('join_tournament')
        self.user = User.objects.get(username='johndoe')
        self.data = {

        }

    # def test_get_join_tournament_redirects_when_not_logged_in(self):
    #     response = self.client.post(self.url)
    #     redirect_url = reverse_with_next('log_in', self.url)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_successful_join_tournament(self):
    #     self.client.login(email=self.user.email, password="Password123")
    #
    #     # We need to test that participant has been created
    #     participant_count_before = Participant.objects.count()
    #
    #     #response = self.client.post(self.url, self.data, follow=True)
    #
    #     participant_count_after = Participant.objects.count()
    #
    #     self.assertEqual(participant_count_after, participant_count_before+1)
    #
    #
    # def test_unsuccessful_create_club(self):
    #     self.client.login(email=self.user.email, password='Password123')
    #
    #     participant_count_before = Participant.objects.count()
    #
    #     # self.data['name'] = ""
    #     # response = self.client.post(self.url, self.data, follow=True)
    #
    #     participant_count_after = Club.objects.count()
    #
    #     self.assertEqual(participant_count_after, participant_count_before)
