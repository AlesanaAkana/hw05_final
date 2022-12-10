from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='auth')

        cls.post = Post.objects.create(
            text='test_post',
            author=cls.user_author,
        )

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user_author)
        cache.clear()

    def test_url_available_to_any_user(self):
        """Страница доступна любому пользователю."""
        url_names = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
        ]
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_unexisting_page(self):
        """Страница не доступна."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_edit_only_for_author(self):
        """Страница /edit/ доступна автору."""
        response = self.authorized_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.reason_phrase, 'OK')

    def test_url_delete_only_for_author(self):
        """Страница /delete/ доступна автору."""
        response = self.authorized_author.get(f'/delete/{self.post.id}/')
        self.assertEqual(response.reason_phrase, 'Found')

    def test_add_comment_only_for_authorized(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse(
            'posts:add_comment', kwargs={'post_id': self.post.id}
        ))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_url_create_for_authorized(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_index_for_authorized(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_only_for_authorized(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user}
        ))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unfollow_only_for_authorized(self):
        """Страница доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user}
        ))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_url_redirect_anonymous_on_admin_login(self):
        """Страница перенаправит анонимного пользователя на страницу логина."""
        url_names = {
            reverse('users:login') + '?next=' + reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}): (
                reverse(
                    'posts:post_edit', kwargs={'post_id': self.post.id}
                )
            ),
            reverse('users:login') + '?next=' + reverse(
                'posts:post_delete', kwargs={'post_id': self.post.id}): (
                reverse(
                    'posts:post_delete', kwargs={'post_id': self.post.id}
                )
            ),
            reverse('users:login') + '?next=' + reverse(
                'posts:post_create'): (
                reverse('posts:post_create')
            ),
            reverse('users:login') + '?next=' + reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id}): (
                reverse(
                    'posts:add_comment', kwargs={'post_id': self.post.id}
                )
            ),
            reverse('users:login') + '?next=' + reverse(
                'posts:follow_index'): (
                reverse('posts:follow_index')
            ),
        }
        for url_full_name, url_name in url_names.items():
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(url_name)
                self.assertRedirects(response, url_full_name)

    def test_url_redirect_for_authorized(self):
        """Страница перенаправит авторизованного пользователя
        на страницу логина.
        """
        url_names = [
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            reverse('posts:post_delete', kwargs={'post_id': self.post.id})
        ]
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                self.assertRedirects(response, reverse(
                    'posts:post_detail', kwargs={'post_id': self.post.id})
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): (
                'posts/group_list.html'
            ),
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): (
                'posts/profile.html'
            ),
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create',): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): (
                'posts/create_post.html'
            ),
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)
