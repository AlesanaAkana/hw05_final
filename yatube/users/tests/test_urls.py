from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
        }
        for address, template in url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        templates_url_names = {
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={'uidb64': 'uidb64', 'token': 'token'}):
                'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'):
                'users/logged_out.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
