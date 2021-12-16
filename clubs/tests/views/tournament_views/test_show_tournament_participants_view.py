"""Test view to fetch participant list of a specific tournament."""

from django.test import TestCase
from django.urls import reverse
from clubs.models import Club, Membership, User, Tournament, Organiser, Participant
from clubs.tests.helpers import reverse_with_next, MenuTesterMixin
from django.conf import settings

from clubs.views.decorators import tournament_exists

class ShowTouramentParticipantsViewTestCase(TestCase, MenuTesterMixin):
    """Test aspects of show tournament participants view"""

    fixtures = [
        'clubs/tests/fixtures/default_club.json',
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_tournament.json',
    ]

    def setUp(self):
        self.owner_user = User.objects.get(username='johndoe')
        self.non_member_user = User.objects.get(username='janedoe')
        self.participant_user = User.objects.get(username='richarddoe')

        self.club = Club.objects.get(name='King\'s Knights')

        self.owner_member = Membership.objects.create(
            club = self.club,
            user = self.owner_user,
            is_owner = True,
        )

        self.participant_member = Membership.objects.create(
            user = self.participant_user,
            club = self.club,
        )

        self.tournament = Tournament.objects.get(name="Grand Championship")

        self.organiser = Organiser.objects.create(
            member = self.owner_member,
            tournament = self.tournament,
            is_lead_organiser = True
        )

        self.participant = Participant.objects.create(
            member = self.participant_member,
            tournament = self.tournament
        )

        self.url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id})

    def test_show_tournament_participants_url(self):
        self.assertEqual(self.url, f'/tournament/{self.tournament.id}/participants')

    def test_show_tournament_participants_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_tournament_participants_with_invalid_id(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self.url = reverse('show_tournament_participants', kwargs={'tournament_id': 999})
        response = self.client.get(self.url)
        redirect_url = reverse("show_clubs")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_show_tournament_participants_redirects_when_not_member(self):
        self.client.login(email=self.non_member_user.email, password="Password123")
        response = self.client.get(self.url)
        redirect_url = reverse("show_club", kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_tournament_participants_with_valid_id(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) #OK
        self.assertTemplateUsed(response, "tournament/show_tournament_participants.html")
        self.assert_menu(response)

    def test_get_show_clubs_with_pagination(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self._create_test_participants(settings.TOURNAMENT_PARTICIPANTS_PER_PAGE*2+3 - 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE)
        clubs_page = response.context['page_obj']
        self.assertFalse(clubs_page.has_previous())
        self.assertTrue(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_one_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE)
        clubs_page = response.context['page_obj']
        self.assertFalse(clubs_page.has_previous())
        self.assertTrue(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_two_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE)
        clubs_page = response.context['page_obj']
        self.assertTrue(clubs_page.has_previous())
        self.assertTrue(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')
        page_three_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 3)
        clubs_page = response.context['page_obj']
        self.assertTrue(clubs_page.has_previous())
        self.assertFalse(clubs_page.has_next())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_clubs_with_pagination_does_not_contain_page_traversers_if_not_enough_clubs(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self._create_test_participants(settings.TOURNAMENT_PARTICIPANTS_PER_PAGE-2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        clubs_page = response.context['page_obj']
        self.assertFalse(clubs_page.has_previous())
        self.assertFalse(clubs_page.has_next())
        self.assertFalse(clubs_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">', 0)

    def test_show_applications_list_with_pagination_creating_page_not_an_integer_error(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self._create_test_participants(settings.TOURNAMENT_PARTICIPANTS_PER_PAGE + 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_incorrect_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=INCORRECTINPUT'
        response = self.client.get(page_incorrect_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        #test we're going back to the first page
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE)
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def test_show_applications_list_with_pagination_creating_empty_page_error_from_bigger_page_number_than_exists(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self._create_test_participants(settings.TOURNAMENT_PARTICIPANTS_PER_PAGE * 2 + 1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_big_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=9999'
        response = self.client.get(page_big_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')


    def test_show_applications_list_with_pagination_creating_empty_page_error_from_smaller_page_number_than_exists(self):
        self.client.login(email=self.owner_user.email, password="Password123")
        self._create_test_participants(settings.TOURNAMENT_PARTICIPANTS_PER_PAGE * 2 + 1) #creating three pages
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_two_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_zero_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=0'
        response = self.client.get(page_zero_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_one_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        self.assertEqual(len(response.context['page_obj']), settings.TOURNAMENT_PARTICIPANTS_PER_PAGE )
        applications_page = response.context['page_obj']
        self.assertFalse(applications_page.has_previous())
        self.assertTrue(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

        page_negative_url = reverse('show_tournament_participants', kwargs={'tournament_id': self.tournament.id}) + '?page=-999'
        response = self.client.get(page_negative_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tournament/show_tournament_participants.html')
        self.assert_menu(response)
        #test we're going to the last page
        self.assertEqual(len(response.context['page_obj']), 2)
        applications_page = response.context['page_obj']
        self.assertTrue(applications_page.has_previous())
        self.assertFalse(applications_page.has_next())
        self.assertTrue(applications_page.has_other_pages())
        self.assertContains(response, '<ul class="pagination ">')

    def _create_test_participants(self, participant_count=10):
        for participant_id in range(participant_count):
            user_participant = User.objects.create(
                username = f'USERNAME{participant_id}',
                last_name = f'LASTNAME{participant_id}',
                first_name = f'FIRSTNAME{participant_id}',
                email = f'EMAIL{participant_id}@gmail.com',
                bio = f'BIO{participant_id}',
                experience = 1
            )

            member_participant = Membership.objects.create(
                club = self.club,
                user = user_participant,
                is_owner = False,
                is_officer = False
            )

            Participant.objects.create(
                member = member_participant,
                tournament = self.tournament
            )