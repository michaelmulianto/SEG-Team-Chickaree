"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User, Club, Member
from clubs.tests.helpers import reverse_with_next

class MembersTestCase(TestCase):
    """Test aspects of account view"""

    fixtures = ['clubs/tests/fixtures/default_user.json',
    'clubs/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.club = Club.objects.get(name='King\'s Knights')

        self.member = Member.objects.create(
            user = self.user,
            club = self.club,
            is_officer = False,
            is_owner = False,
        )
        self.url = reverse('members_list', kwargs={'club_id': self.club.id})

    def test_members_list_url(self):
        self.assertEqual('/members_list/'+ str(self.club.id), self.url)

    def test_get_user_list_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_members_list(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_list.html')

    def _create_test_users(self, user_count=10):
        for user_id in range(user_count):
            users = User.objects.create_user(
                f'@user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
            )
            Member.objects.create(
                user = users,
                club = self.club,
                is_officer = False,
                is_owner = False,
            )
