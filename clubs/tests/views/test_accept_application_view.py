"""Test backend implementation of the ability to accept applications."""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from clubs.models import User, Club, Member, Application
from clubs.tests.helpers import reverse_with_next

class AcceptApplicationTestCase(TestCase):
    """Test all aspects of the show applications to club view"""

    fixtures = ['clubs/tests/fixtures/default_user.json']
    fixtures = ['clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.applyingUser = User.objects.get(username='johndoe')
        self.ownerUser = User.objects.create(
            username = 'janedoe',
            first_name = 'Jane',
            last_name = 'Doe',
            email = 'janedoe@example.com',
            password='Password123'
        )

        self.club = Club.objects.get(name='Chess Clubs')

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

    def test_accept_application_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_accept_application_redirects_when_not_owner_of_club(self):
        self.membership.isOwner = False
        self.membership.save(update_fields=['isOwner'])

        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')
    
    def test_show_application_to_club_redirects_when_invalid_club_id_entered(self):
        self.url = reverse('show_applications_to_club', kwargs = {'club_id': 0})
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('show_clubs')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_clubs.html')

    def test_successful_show_applications_to_club(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)

        response_url = self.url
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application_list.html')