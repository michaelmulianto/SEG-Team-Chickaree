"""
Test backend implementation of the ability for tournament lead organisers to add officers/owners of
their club to an organiser of said tournament.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import Organiser, Participant, Tournament, User, Club, Membership
from django.core.exceptions import ObjectDoesNotExist
from clubs.tests.helpers import reverse_with_next
from django.contrib import messages

from clubs.views.decorators import tournament_exists

class AddOrganiserToTournamentViewTestCase(TestCase):
    """Test all aspects of the backend implementation of promoting members"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_tournament.json',
        'clubs/tests/fixtures/other_tournaments.json'
    ]

    def setUp(self):
        self.owner_user = User.objects.get(username='johndoe')
        self.officer_user = User.objects.get(username='richarddoe')
        self.regular_user = User.objects.get(username='janedoe')

        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
            is_officer = False
        )
        self.officer_member = Membership.objects.create(
            club = self.club,
            user = self.officer_user,
            is_owner = False,
            is_officer = True
        )

        self.regular_member = Membership.objects.create(
            club = self.club,
            user = self.regular_user,
            is_owner = False,
            is_officer = False,
        )

        self.tournament_owner_organiser = Tournament.objects.get(name="Grand Championship")
        Organiser.objects.create(
            member = self.owner_member,
            tournament = self.tournament_owner_organiser,
            is_lead_organiser = True
        )

        self.tournament_officer_organiser = Tournament.objects.get(name="Just A League")
        Organiser.objects.create(
            member = self.officer_member,
            tournament = self.tournament_officer_organiser,
            is_lead_organiser = True
        )

        self.url_owner_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id, 'member_id': self.officer_member.id})
        self.url_officer_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id, 'member_id': self.owner_member.id})

    def test_assign_organiser_url_owner_organiser(self):
        self.assertEqual(self.url_owner_organiser, f'/tournament/{self.tournament_owner_organiser.id}/add_organiser/{self.officer_member.id}')
    
    def test_assign_organiser_url_officer_organiser(self):
        self.assertEqual(self.url_officer_organiser, f'/tournament/{self.tournament_officer_organiser.id}/add_organiser/{self.owner_member.id}')

    def test_assign_organiser_redirects_when_not_logged_in_from_owner_organiser(self):
        response = self.client.get(self.url_owner_organiser)
        redirect_url = reverse_with_next('log_in', self.url_owner_organiser)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.officer_member))

    def test_assign_organiser_redirects_when_not_logged_in_from_officer_organiser(self):
        response = self.client.get(self.url_officer_organiser)
        redirect_url = reverse_with_next('log_in', self.url_officer_organiser)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.owner_member))

    def test_assign_organiser_redirects_when_invalid_tournament_id_entered_form_owner_organiser(self):
        self.url_owner_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': 999, 'member_id':self.officer_member.id})
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url_owner_organiser, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.officer_member))

    def test_assign_organiser_redirects_when_invalid_tournament_id_entered_form_officer_organiser(self):
        self.url_officer_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': 999, 'member_id':self.owner_member.id})
        self.client.login(email=self.officer_user.email, password="Password123")
        response = self.client.get(self.url_officer_organiser, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.owner_member))

    def test_assign_organiser_redirects_when_invalid_member_id_entered_from_owner_organiser(self):
        self.url_owner_organiser = reverse('add_organiser_to_tournament', kwargs = {'member_id': 999, 'tournament_id': self.tournament_owner_organiser.id})
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url_owner_organiser, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.officer_member))

    def test_assign_organiser_redirects_when_invalid_member_id_entered_from_officer_organiser(self):
        self.url_officer_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id, 'member_id': 999 })
        self.client.login(email=self.officer_user.email, password="Password123")
        response = self.client.get(self.url_officer_organiser, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club/show_clubs.html')
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.owner_member))

    def test_assign_organiser_redirects_when_not_lead_organiser_of_tournament_from_owner_organiser(self):
        self.client.login(email=self.regular_user.email, password="Password123")
        response = self.client.get(self.url_owner_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id' : self.tournament_owner_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.regular_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_assign_organiser_redirects_when_not_lead_organiser_of_tournament_from_officer_organiser(self):
        self.client.login(email=self.regular_user.email, password="Password123")
        response = self.client.get(self.url_officer_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.regular_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_assign_organiser_redirects_when_organiser_assigning_themselves_from_owner_organiser(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.url_owner_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id, 'member_id': self.owner_member.id })
        response = self.client.get(self.url_owner_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.owner_member))
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_owner_organiser, membership = self.owner_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_assign_organiser_redirects_when_organiser_assigning_themselves_from_officer_organiser(self):
        self.client.login(email=self.officer_user.email, password="Password123")
        self.url_officer_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id, 'member_id': self.officer_member.id })
        response = self.client.get(self.url_officer_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.officer_member))
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_officer_organiser, membership = self.officer_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_assign_organiser_redirects_when_assigning_organiser_to_a_regular_member_from_owner_organiser(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.url_owner_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id, 'member_id': self.regular_member.id })
        response = self.client.get(self.url_owner_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.owner_member))
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_owner_organiser, membership = self.owner_member))
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.regular_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_assign_organiser_redirects_when_assigning_organiser_to_a_regular_member_from_officer_organiser(self):
        self.client.login(email=self.officer_user.email, password="Password123")
        url_add_regular_member_as_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id, 'member_id': self.regular_member.id })
        response = self.client.get(url_add_regular_member_as_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.officer_member))
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_officer_organiser, membership = self.officer_member))
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.regular_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_assign_organiser_redirects_when_assigning_organiser_to_a_participant_from_owner(self):
        new_participant = Participant.objects.create(
            member = self.officer_member,
            tournament = self.tournament_owner_organiser
        )
        new_participant.save()
        
        self.client.login(email=self.owner_user.email, password="Password123")
        self.url_owner_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id, 'member_id': self.officer_member.id })
        response = self.client.get(self.url_owner_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.owner_member))
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_owner_organiser, membership = self.owner_member))
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.officer_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_assign_organiser_redirects_when_assigning_organiser_to_a_participant_from_officer(self):
        new_participant = Participant.objects.create(
            member = self.owner_member,
            tournament = self.tournament_officer_organiser
        )
        new_participant.save()
        
        self.client.login(email=self.officer_user.email, password="Password123")
        self.url_officer_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id, 'member_id': self.owner_member.id })
        response = self.client.get(self.url_officer_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.officer_member))
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_officer_organiser, membership = self.officer_member))
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.owner_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.WARNING)

    def test_successful_assign_organiser_to_from_owner_organiser_to_officer(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_owner_organiser, membership = self.owner_member))
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.officer_member))
        response = self.client.get(self.url_owner_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_owner_organiser, membership = self.officer_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_successful_assign_organiser_to_from_officer_organiser_to_owner(self):
        self.client.login(email=self.officer_user.email, password="Password123")
        self.assertTrue(self._is_member_lead_organiser(tournament = self.tournament_officer_organiser, membership = self.officer_member))
        self.assertFalse(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.owner_member))
        response = self.client.get(self.url_officer_organiser, follow=True)
        redirect_url = reverse('show_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tournament/show_tournament.html')
        self.assertTrue(self._is_member_organiser(tournament = self.tournament_officer_organiser, membership = self.owner_member))

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def _is_member_organiser(self, tournament, membership):
            return Organiser.objects.filter(member = membership, tournament = tournament).exists()

    def _is_member_lead_organiser(self, tournament, membership):
            return Organiser.objects.filter(member = membership, tournament = tournament, is_lead_organiser=True).exists()