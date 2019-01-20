import json
from rest_framework.test import APITestCase
from social_network.models import UserProfile, Post

BASE_URL = 'http://127.0.0.1:8000/api/'


class TestSocialEndpoints(APITestCase):

    token = ''

    def setUp(self):
        self.user = UserProfile.objects.create_user(username='some_username',
                                                    email='some_email@email.com',
                                                    password='some_password')
        self.post = Post.objects.create(text='Obviously I am just testing a post creation..',
                                        user=self.user)

        response = self.client.post(BASE_URL + 'token-auth/',
                                    {'username': 'some_username', 'password': 'some_password'},
                                    format='json')
        resp = json.loads(response.content)
        self.token = resp['token']

    def test_sign_up(self):
        data = {
            'username': 'some_username2',
            'email': 'some_email2@email.com',
            'password': 'some_password',
            'confirm_password': 'some_password'
        }

        response = self.client.post(BASE_URL + 'sign-up/', data, format='json')
        resp = json.loads(response.content)

        assert resp['username'] == data['username']
        assert resp['email'] == data['email']
        assert UserProfile.objects.get(username=data['username']).username == 'some_username2'
        assert UserProfile.objects.get(email=data['email']).email == 'some_email2@email.com'

    def test_sign_up_with_wrong_pass_confirmation(self):
        data = {
            'username': 'some_username2',
            'email': 'some_email2@email.com',
            'password': 'some_password',
            'confirm_password': 'ololo'
        }

        response = self.client.post(BASE_URL + 'sign-up/', data, format='json')
        resp = json.loads(response.content)
        assert resp['non_field_errors'] == ['Passwords are not the same']

    def test_user_list_without_doing_login(self):
        url = BASE_URL + 'user/'
        response = self.client.get(url)
        resp = json.loads(response.content)
        assert resp['detail'] == 'Authentication credentials were not provided.'

    def test_user_list(self):
        url = BASE_URL + 'user/'
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        response = self.client.get(url)
        resp = json.loads(response.content)
        assert len(resp['results']) == 1

    def test_user_page(self):
        url = BASE_URL + 'user/1/'
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        response = self.client.get(url)
        resp = json.loads(response.content)
        assert resp['id'] == 1
        assert resp['username'] == 'some_username'

    def test_post_like(self):
        url = BASE_URL + 'post/1/like_dislike/'
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        response = self.client.post(url, {'action_type': 'like'}, format='json')
        resp = json.loads(response.content)
        assert resp['message'] == '''like is set to some_username's post'''

        post = Post.objects.get(id=1)
        assert post.like == 1

    def test_post_dislike(self):
        url = BASE_URL + 'post/1/like_dislike/'
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        response = self.client.post(url, {'action_type': 'dislike'}, format='json')
        resp = json.loads(response.content)
        assert resp['message'] == '''dislike is set to some_username's post'''

        post = Post.objects.get(id=1)
        assert post.dislike == 1

    def test_post_creation(self):
        posts = Post.objects.all()
        assert len(posts) == 1

        url = BASE_URL + 'post/'
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        self.client.post(url, {'text': 'Another weird post'}, format='json')

        posts = Post.objects.all()
        assert len(posts) == 2

    def test_posts_list(self):
        url = BASE_URL + 'post/'
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)
        response = self.client.get(url)
        resp = json.loads(response.content)
        assert len(resp['results']) == 1

    def test_post_list_without_doing_login(self):
        url = BASE_URL + 'post/'
        response = self.client.get(url)
        resp = json.loads(response.content)
        assert resp['detail'] == 'Authentication credentials were not provided.'
