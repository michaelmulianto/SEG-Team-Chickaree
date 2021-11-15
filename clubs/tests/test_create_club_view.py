# # """Test user-facing implementation of the create club form."""
#
# from django.test import TestCase
# from django.urls import reverse
# from clubs.models import User, Club
# from clubs.forms import SignUpForm
# from django.contrib.auth.hashers import check_password
#
# class CreateClubViewTest(TestCase):
#     """Test all aspects of the create club view"""
#
#     def setUp(self):
#         self.url = reverse('sign_up')
#         self.form_input = {
#         'first_name': 'Jane',
#         'last_name': 'Doe',
#         'username': 'janedoe',
#         'email': 'janedoe@example.org',
#         'new_password': 'Password123',
#         'password_confirmation': 'Password123'
#         }
#
#     def test_create_club_url(self):
#         self.assertEqual(self.url, '/create_club/')
#
#     def test_get_create_club(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200) #OK
#         self.assertTemplateUsed(response, 'create_club.html')
#         form = response.context['form']
#         self.assertTrue(isinstance(form, CreateClubForm))
#         self.assertFalse(form.is_bound)
#
#     def test_create_club_redirects_when_not_logged_in(self):
#         user_count_before = Club.objects.count()
#         redirect_url = reverse('log_in')
#         response = self.client.post(self.url, self.data, follow=True)
#         self.assertRedirects(response, redirect_url,
#             status_code=302, target_status_code=200, fetch_redirect_response=True
#         )
#         user_count_after = Club.objects.count()
#         self.assertEqual(user_count_after, user_count_before)
#
#     def test_successful_create_club(self):
#         #self.client.login(username=self.user.username, password="Password123")   uncomment when login is implemented
#         before_count = Club.objects.count()
#         response = self.client.post(self.url, self.form_input, follow=True)
#         after_count = Club.objects.count()
#         self.assertEqual(after_count, before_count+1)
#         new_club = Club.objects.latest('created_on')
#         self.assertEqual(self.user, new_club.owner)
#         response_url = reverse('feed')
#         self.assertRedirects(
#             response, response_url,
#             status_code=302, target_status_code=200,
#             fetch_redirect_response=True
#         )
#         self.assertTemplateUsed(response, 'create_club.html')
