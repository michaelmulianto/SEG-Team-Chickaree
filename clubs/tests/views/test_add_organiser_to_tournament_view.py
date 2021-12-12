"""
Test backend implementation of the ability for tournament lead organisers to add officers/owners of
their club to an organiser of said tournament.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import Organiser, Tournament, User, Club, Membership
from clubs.tests.helpers import reverse_with_next

class PromoteMemberToOfficerViewTestCase(TestCase):
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
        self.target_user = User.objects.get(username='janedoe')
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
            user = self.target_user,
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

        self.url_owner_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_owner_organiser, 'member_id': self._member.id})
        self.url_officer_organiser = reverse('add_organiser_to_tournament', kwargs = {'tournament_id': self.tournament_officer_organiser, 'member_id': self._member.id})

    def test_assign_organiser_url_owner_organiser(self):
        self.assertEqual(self.url_owner_organiser, f'/tournament/{self.tournament_owner_organiser.id}/add_organiser/{self.officer_member.id}')
    
    def test_assign_organiser_url_officer_organiser(self):
        self.assertEqual(self.url_officer_organiser, f'/tournament/{self.tournament_officer_organiser.id}/add_organiser/{self.owner_member.id}')

    def test_assign_organiser_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertFalse(self._is_member_organiser(self.target_member.id))

    def test_assign_organiser_redirects_when_invalid_tournament_id_entered(self):
        self.url = reverse('promote_member_to_officer', kwargs = {'tournament_id': 999, 'member_id':self.officer_member.id})
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._is_member_organiser(self.target_member.id))

    def test_assign_organiser_redirects_when_invalid_member_id_entered(self):
        self.url = reverse('promote_member_to_officer', kwargs = {'member_id': 999})
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
        self.assertFalse(self._is_member_organiser(self.target_member.id))

    def test_assign_organiser_redirects_when_not_organiser_of_tournament(self):
        self.client.login(email=self.target_user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertFalse(self._is_member_organiser(self.target_member.id))

    def test_assign_organiser_redirects_when_owner_assigning_themselves(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        url_promote_owner = reverse('promote_member_to_officer', kwargs = {'member_id': self.owner_member.id})
        response = self.client.get(url_promote_owner, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertFalse(self._is_member_organiser(self.owner_member.id))

    def test_assign_organiser_redirects_when_assigning_organiser_to_a_regular_member_from_owner_organiser(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        url_promote_officer = reverse('promote_member_to_officer', kwargs = {'member_id': self.officer_member.id})
        response = self.client.get(url_promote_officer, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._is_member_organiser(self.officer_member.id))

    def test_assign_organiser_redirects_when_assigning_organiser_to_a_regular_member_from_officer_organiser(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        url_promote_officer = reverse('promote_member_to_officer', kwargs = {'member_id': self.officer_member.id})
        response = self.client.get(url_promote_officer, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._is_member_organiser(self.officer_member.id))

    def test_successful_assign_organiser_to_owner(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.assertFalse(self._is_member_organiser(self.target_member.id))
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._is_member_organiser(self.target_member.id))

    def test_successful_assign_organiser_to_officer(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.assertFalse(self._is_member_organiser(self.target_member.id))
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('members_list', kwargs = {'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertTrue(self._is_member_organiser(self.target_member.id))

    def _is_member_organiser(self, tournament, member):
        return Organiser.objects.get(member = member, tournament = tournament).exists()

    def _is_member_lead_organiser(self, tournament, member):
        return Organiser.objects.get(member = member, tournament = tournament).is_lead_organiser

