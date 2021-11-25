"""Test backend implementation of the ability to accept/reject applications."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member, Application
from clubs.tests.helpers import reverse_with_next

class RespondToApplicationViewTestCase(TestCase):
    """Test all aspects of the respond to applications view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']

    def setUp(self):
        self.ownerUser = User.objects.get(username='johndoe')
        self.applyingUser = User.objects.create(
            username = 'janedoe',
            first_name = 'Jane',
            last_name = 'Doe',
            email = 'janedoe@example.com',
            password='Password123'
        )

        self.club = Club.objects.create(
            name = 'Kings Knight',
            location = 'Kings College',
            description = 'best club in the world'
        )

        self.ownerMember = Member.objects.create(
            club = self.club,
            user = self.ownerUser,
            isOwner = True
        )

        self.application = Application.objects.create(
            club = self.club,
            user = self.applyingUser,
            experience = 2,
            personalStatement = 'I love chess!' 
        )

        self.url = reverse('respond_to_application', kwargs = {'app_id': self.application.id, 'is_accepted': 1})

    def test_respond_to_app_url(self):
        self.assertEqual(self.url, '/application/' + str(self.application.id) + "/respond/1")

    def test_respond_to_application_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_respond_to_application_redirects_when_not_owner_of_club(self):
        self.ownerMember.isOwner = False
        self.ownerMember.save(update_fields=['isOwner'])

        self.client.login(username=self.ownerUser.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
    
    def test_respond_to_application_redirects_when_invalid_application_id_entered(self):
        self.url = reverse('respond_to_application', kwargs = {'app_id': 0, 'is_accepted':1})
        self.client.login(username=self.ownerUser.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_successful_accept_application_to_club(self):
        self.client.login(username=self.ownerUser.username, password="Password123")

        member_count_before = Member.objects.count()
        application_count_before = Application.objects.count()

        response = self.client.get(self.url, follow=True)

        member_count_after = Member.objects.count()
        application_count_after = Application.objects.count()

        self.assertEqual(member_count_before, member_count_after-1)
        self.assertEqual(application_count_before, application_count_after+1)

        response_url = reverse('show_applications_to_club', kwargs={'club_id':self.club.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_list.html')
