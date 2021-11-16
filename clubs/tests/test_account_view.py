"""Unit test for the feed view"""

from django.test import TestCase
from django.urls import reverse
from clubs.models import User

class AccountViewTestCase(TestCase):
    """To be implemented, code stolen from clucker, change feed for account and edit"""
    pass

    # def setUp(self):
    #     self.url = reverse('feed')
    #     self.form_input = {
    #         'text': 'just setting up my clckr'
    #     }
    #     self.user = User.objects.create_user(
    #         '@johndoe',
    #         first_name = 'John',
    #         last_name = 'Doe',
    #         email = 'johndoe@example.org',
    #         password = 'Password123',
    #         is_active=True
    #     )
    #     self.client.login(username='@johndoe', password='Password123')
    #
    #
    # def test_get_feed_url(self):
    #     self.assertEqual('/feed/', self.url)
    #
    # def test_get_feed_logged_in_user(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'feed.html')
    #
    #     post_list = list(response.context['post_list'])
    #     self.assertTrue(isinstance(post_list, list))
    #     self.assertEqual(len(post_list), len(Post.objects.all()))
    #
    # def test_successful_new_post(self):
    #     before_count = Post.objects.count()
    #     response = self.client.post(self.url, self.form_input, follow=True)
    #     after_count = Post.objects.count()
    #     self.assertEqual(before_count+1, after_count)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'feed.html')
    #     post_form = response.context['post_form']
    #     self.assertTrue(isinstance(post_form, PostForm))
    #     self.assertFalse(post_form.is_bound)
    #
    # def test_bad_input_new_post(self):
    #     self.form_input['text'] = 'x' * 300
    #     response = self.client.post(self.url, self.form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'feed.html')
    #     post_form = response.context['post_form']
    #     self.assertTrue(isinstance(post_form, PostForm))
    #     self.assertFalse(post_form.is_bound)
    #
    # def test_new_post_cannot_be_blank(self):
    #     self.form_input['text'] = ''
    #     response = self.client.post(self.url, self.form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'feed.html')
    #     post_form = response.context['post_form']
    #     self.assertTrue(isinstance(post_form, PostForm))
    #     self.assertFalse(post_form.is_bound)
    #
    # def test_user_not_logged_in_cannot_create_post(self):
    #     self.client.logout()
    #     response = self.client.post(self.url, self.form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'feed.html')
    #     post_form = response.context['post_form']
    #     self.assertTrue(isinstance(post_form, PostForm))
    #     self.assertFalse(post_form.is_bound)
    #
    #     self.client.login(username='@johndoe', password='Password123') #log back in just in case for other tests
