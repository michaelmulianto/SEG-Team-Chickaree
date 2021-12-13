"""Test backend implementation of the ability to accept/reject applications."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Membership, Application
from clubs.tests.helpers import reverse_with_next

class RespondToApplicationViewTestCase(TestCase):
    """Test all aspects of the respond to applications view"""

    fixtures = [
        'clubs/tests/fixtures/default_user.json',
        'clubs/tests/fixtures/other_users.json',
        'clubs/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.user_club_owner = User.objects.get(username='johndoe')
        self.user_club_officer = User.objects.get(username='richarddoe')
        self.user_club_applicant = User.objects.get(username='janedoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member_club_owner = Membership.objects.create(
            club = self.club,
            user = self.user_club_owner,
            is_owner = True
        )
        self.member_club_officer = Membership.objects.create(
            club = self.club,
            user = self.user_club_officer,
            is_officer = True
        )

        self.application = Application.objects.create(
            club = self.club,
            user = self.user_club_applicant,
            personal_statement = 'I love chess!'
        )

        self.url_accepted = reverse('respond_to_application', kwargs = {'app_id': self.application.id, 'is_accepted': 1})
        self.url_rejected = reverse('respond_to_application', kwargs = {'app_id': self.application.id, 'is_accepted':0})


    def test_respond_to_app_url(self):
        self.assertEqual(self.url_accepted, f'/application/{self.application.id}/respond/1/')
        self.assertEqual(self.url_rejected, f'/application/{self.application.id}/respond/0/')

    def test_respond_to_application_redirects_when_not_logged_in(self):
        response = self.client.get(self.url_accepted)
        redirect_url = reverse_with_next('log_in', self.url_accepted)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_respond_to_application_redirects_when_invalid_application_id_entered(self):
        url_invalid_id = reverse('respond_to_application', kwargs = {'app_id': 0, 'is_accepted':1})
        self.client.login(email=self.user_club_owner.email, password="Password123")
        response = self.client.get(url_invalid_id, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_respond_to_application_redirects_when_not_owner_or_officer_of_club(self):
        self.client.login(email=self.user_club_applicant.email, password="Password123")
        response = self.client.get(self.url_accepted, follow=True)

        redirect_url = reverse('show_club', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_club.html')

    def test_successful_accept_application_to_club_owner(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")

        member_count_before = Membership.objects.count()
        application_count_before = Application.objects.count()

        response = self.client.get(self.url_accepted, follow=True)
        member_count_after = Membership.objects.count()
        application_count_after = Application.objects.count()

        self.assertEqual(member_count_before, member_count_after-1)
        self.assertEqual(application_count_before, application_count_after+1)

        redirect_url = reverse('show_applications_to_club', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'application_list.html')

    def test_successful_reject_application_to_club_owner(self):
        self.client.login(email=self.user_club_owner.email, password="Password123")

        member_count_before = Membership.objects.count()
        application_count_before = Application.objects.count()

        response = self.client.get(self.url_rejected, follow=True)

        member_count_after = Membership.objects.count()
        application_count_after = Application.objects.count()

        self.assertEqual(member_count_before, member_count_after)
        self.assertEqual(application_count_before, application_count_after+1)

        response_url = reverse('show_applications_to_club', kwargs={'club_id':self.club.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_list.html')

    def test_successful_accept_application_to_club_officer(self):
        self.client.login(email=self.user_club_officer.email, password="Password123")

        member_count_before = Membership.objects.count()
        application_count_before = Application.objects.count()

        response = self.client.get(self.url_accepted, follow=True)
        member_count_after = Membership.objects.count()
        application_count_after = Application.objects.count()

        self.assertEqual(member_count_before, member_count_after-1)
        self.assertEqual(application_count_before, application_count_after+1)

        redirect_url = reverse('show_applications_to_club', kwargs={'club_id':self.club.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'application_list.html')

    def test_successful_reject_application_to_club_officer(self):
        self.client.login(email=self.user_club_officer.email, password="Password123")

        member_count_before = Membership.objects.count()
        application_count_before = Application.objects.count()

        response = self.client.get(self.url_rejected, follow=True)

        member_count_after = Membership.objects.count()
        application_count_after = Application.objects.count()

        self.assertEqual(member_count_before, member_count_after)
        self.assertEqual(application_count_before, application_count_after+1)

        response_url = reverse('show_applications_to_club', kwargs={'club_id':self.club.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_list.html')
