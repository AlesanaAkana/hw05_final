from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User
from users.forms import CreationForm


class CreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_signup_form(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()

        form_data = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'test_email@mail.ru',
            'password1': 'this_is_password',
            'password2': 'this_is_password',
        }
        response = self.guest_client.post(
            reverse('users:signup'), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(username='test_username').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)
