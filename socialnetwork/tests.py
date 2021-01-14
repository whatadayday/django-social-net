from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
try:
    from django.core.urlresolvers import reverse
except ImportError:  # django < 1.10
    from django.urls import reverse
from django.test import Client
from socialnetwork.models import User, Post
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User

USER_EMAIL = 'test@gmail.com'
USER_PASSWD = 'verysecurepassword'

# Create your tests here.
class BasicTest(APITestCase):
    def setUp(self):
        self.c = APIClient()
        user = User.objects.create_user(USER_EMAIL, USER_PASSWD)
        url = reverse('token_obtain_pair')
        response = self.c.post(url, {'email': USER_EMAIL, 'password': USER_PASSWD})
        self.access = response.json().get('access')

        self.c.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access)

        post = Post.objects.create(title='Lazy dog', body='The quick brown fox jumps over the lazy dog', creator=user)
        self.post_id = post.id

        user2 = User.objects.create_user('test2@gmail.com', USER_PASSWD)
        post2 = Post.objects.create(title='Lazy dog', body='The quick brown fox jumps over the lazy dog', creator=user2)
        self.post2_id = post2.id

    def test_sign_up(self):
        url = reverse('signup')
        response = self.c.post(url, {'email': 'test3@gmail.com', 'password': USER_PASSWD})
        self.assertEqual(response.status_code, 201)
        response = self.c.post(url, {'email': 'test@blablabla', 'password': USER_PASSWD})
        self.assertEqual(response.status_code, 400)

    def test_user_has_clearbit_data(self):
        url = reverse('signup')
        response = self.c.post(url, {'email': 'alex@clearbit.com', 'password': USER_PASSWD})
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='alex@clearbit.com')
        if user.person_info:
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    def test_token_obtain(self):
        url = reverse('token_obtain_pair')
        response = self.c.post(url, {'email': USER_EMAIL, 'password': USER_PASSWD})
        if response.json().get('refresh') and response.json().get('access'):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_post_create(self):
        url = reverse('post_new')
        response = self.c.post(url, {'title': 'Lazy dog', 'body': 'The quick brown fox jumps over the lazy dog'})
        if response.status_code == 201 and response.json().get('id'):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_post_like(self):
        # Try to like own post
        url = reverse('post_like', kwargs={'post_id': self.post_id})
        response = self.c.get(url)
        resp_json = response.json()
        self.assertEqual(response.status_code, 400)

        # Try to like another user post
        url = reverse('post_like', kwargs={'post_id': self.post2_id})
        response = self.c.get(url)
        resp_json = response.json()
        self.assertEqual(response.status_code, 200)

        # Try to like another user post one more time
        url = reverse('post_like', kwargs={'post_id': self.post2_id})
        response = self.c.get(url)
        resp_json = response.json()
        self.assertEqual(response.status_code, 400)

        # Try to unlike another user post
        url = reverse('post_unlike', kwargs={'post_id': self.post2_id})
        response = self.c.get(url)
        resp_json = response.json()
        self.assertEqual(response.status_code, 200)

        # Try to unlike another user post one more time
        url = reverse('post_unlike', kwargs={'post_id': self.post2_id})
        response = self.c.get(url)
        resp_json = response.json()
        self.assertEqual(response.status_code, 400)
