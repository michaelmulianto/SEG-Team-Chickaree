"""Test backend of the organise tournament form."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Organiser, User, Club, Tournament, Membership
from clubs.forms import OrganiseTournamentForm
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.contrib import messages


class OrganiseTournamentViewTest(TestCase, MenuTesterMixin):
    """Test all aspects of the organise tournament view"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
            'clubs/tests/fixtures/default_club.json',
            'clubs/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.second_user = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')
        self.data = {
        "name" : "Grandest Championship",
        "description" : "The most prestigious tournament in London.",
        "capacity" : 16,
        "start" : "2099-12-11T00:00:00+00:00",
        "end" : "2099-12-20T00:00:00+00:00",
        "deadline" : "2099-12-10T00:00:00+00:00",
        }
        self.url = reverse('organise_tournament', kwargs={'club_id': self.club.id})

    def test_organise_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/organise_tournament/')

    def test_get_organise_tournament_loads_empty_form(self):
        self.client.login(email=self.user.email, password="Password123")
        tournament_count_before = Tournament.objects.count()
        response = self.client.get(self.url, follow=True)
        self.assert_menu(response)
        tournament_count_after = Tournament.objects.count()
        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertEqual(response.status_code, 200)

    def test_get_organise_tournament_redirects_when_not_logged_in(self):
        response = self.client.post(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_organise_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        member = Membership.objects.create(
             user=self.user,
             club=self.club,
             is_owner=True
        )
        tournament_count_before = Tournament.objects.count()
        organiser_count_before = Organiser.objects.count()

        response = self.client.post(self.url, self.data, follow=True)

        tournament_count_after = Tournament.objects.count()
        organiser_count_after = Organiser.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before+1)
        self.assertEqual(organiser_count_after, organiser_count_before+1)
        new_tournament = Tournament.objects.all()[0]
        organiser = Organiser.objects.get(member = member, tournament = new_tournament )
        self.assertTrue(member.is_owner)
        self.assertFalse(member.is_officer)
        self.assertEqual(organiser.member, member)
        self.assertTrue(organiser.is_lead_organiser)

        # Response tests
        response_url = reverse('show_club', kwargs={'club_id':self.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_club.html')
        
        
    def test_successful_officer_organise_tournament(self):
        self.client.login(email=self.user.email, password="Password123")
        Membership.objects.create(
            user = self.second_user,
            club = self.club,
            is_owner = True
        )
        member_officer = Membership.objects.create(
             user=self.user,
             club=self.club,
             is_officer=True
        )
        tournament_count_before = Tournament.objects.count()
        organiser_count_before = Organiser.objects.count()
        
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        organiser_count_after = Organiser.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before+1)
        self.assertEqual(organiser_count_after, organiser_count_before+1)
        new_tournament = Tournament.objects.all()[0]
        organiser = Organiser.objects.get(member = member_officer, tournament = new_tournament )
        self.assertFalse(member_officer.is_owner)
        self.assertTrue(member_officer.is_officer)
        self.assertEqual(organiser.member, member_officer)
        self.assertTrue(organiser.is_lead_organiser)

        # Response tests
        response_url = reverse('show_club', kwargs={'club_id':self.club.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_club.html')



    def test_unsuccessful_create_tournament(self):
        self.client.login(email=self.user.email, password='Password123')
        Membership.objects.create(
             user=self.user,
             club=self.club,
             is_officer=True
        )
        tournament_count_before = Tournament.objects.count()
        organiser_count_before = Organiser.objects.count()
        self.data['name'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        organiser_count_after = Organiser.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertEqual(organiser_count_before, organiser_count_after)
        self.assertTemplateUsed(response, 'organise_tournament.html')

    def test_unsuccessful_member_create_tournament(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        organiser_count_before = Organiser.objects.count()
        
        Membership.objects.create(
             user=self.user,
             club=self.club
        )

        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()
        organiser_count_after = Organiser.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertEqual(organiser_count_before, organiser_count_after)
        self.assertTemplateUsed(response, 'organise_tournament.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_start_time_in_past_fails(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['start'] = "1999-12-11T00:00:00+00:00"
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertTemplateUsed(response, 'organise_tournament.html')

    def test_end_time_in_past_fails(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['end'] = "1999-12-11T00:00:00+00:00"
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertTemplateUsed(response, 'organise_tournament.html')

    def test_deadline_time_in_past_fails(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['deadline'] = "1999-12-11T00:00:00+00:00"
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertTemplateUsed(response, 'organise_tournament.html')

    def test_start_time_in_past_fails(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['start'] = "1999-12-11T00:00:00+00:00"
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertTemplateUsed(response, 'organise_tournament.html')

    def test_end_time_in_past_fails(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['end'] = "1999-12-11T00:00:00+00:00"
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertTemplateUsed(response, 'organise_tournament.html')

    def test_deadline_time_in_past_fails(self):
        self.client.login(email=self.user.email, password='Password123')
        tournament_count_before = Tournament.objects.count()
        self.data['deadline'] = "1999-12-11T00:00:00+00:00"
        response = self.client.post(self.url, self.data, follow=True)
        tournament_count_after = Tournament.objects.count()

        self.assertEqual(tournament_count_after, tournament_count_before)
        self.assertTemplateUsed(response, 'organise_tournament.html')