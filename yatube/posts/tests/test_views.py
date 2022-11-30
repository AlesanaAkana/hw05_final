import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.user_author,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user_author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'auth'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'
            ),
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        templates_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                first_object = response.context['page_obj'][0]
                post_author_0 = first_object.author.username
                post_text_0 = first_object.text
                post_group_0 = first_object.group.title
                post_gpoup_slug_0 = first_object.group.slug
                post_description_0 = first_object.group.description
                post_image_0 = first_object.image
                self.assertEqual(post_author_0, 'auth')
                self.assertEqual(post_text_0, 'test_post')
                self.assertEqual(post_group_0, 'test_group')
                self.assertEqual(post_gpoup_slug_0, 'test_slug')
                self.assertEqual(post_description_0, 'test_description')
                self.assertEqual(post_image_0, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertEqual(response.context.get('post').text, 'test_post')
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_create_post_edit_show_correct_context(self):
        """Шаблоны create и post_edit сформирован с правильным контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(
                    reverse('posts:post_create'))
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                response = self.authorized_author.get(
                    reverse('posts:post_edit', kwargs={'post_id': 1}))
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_add_comment_for_guest(self):
        """Проверка add_comment для неавторизованно пользователя."""
        form_data = {'text': 'text'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        redirect = reverse('users:login') + '?next=' + reverse(
            'posts:add_comment', args=(self.post.id,)
        )
        self.assertRedirects(response, redirect)

    def test_add_comment_for_authorized_client(self):
        """Проверка add_comment для авторизованно пользователя."""
        form_data = {
            'text': 'test_comment',
            'author': self.user,
            'post': self.post
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form_data,
        )
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, 'test_comment')

    def test_cache(self):
        """Проверка работы кэша."""
        post = Post.objects.create(
            text='test_post_for_cache',
            author=self.user
        )
        add_content = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        delete_content = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(add_content, delete_content)
        cache.clear()
        cache_clear_content = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(add_content, cache_clear_content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        for i in range(13):
            Post.objects.create(
                text='Тестовый пост #{i}',
                author=cls.user_author,
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_paginator_on_pages(self):
        first_page = 10
        second_page = 3
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for reverse_ in url_pages:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(len(self.guest_client.get(
                    reverse_).context.get('page_obj')),
                    first_page
                )
                self.assertEqual(len(self.guest_client.get(
                    reverse_ + '?page=2').context.get('page_obj')),
                    second_page
                )


class ForCheckingPostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.group_1 = Group.objects.create(
            title='test_group_1',
            slug='test_slug_1',
            description='test_description_1',
        )
        cls.post = Post.objects.create(
            text='test_post',
            author=cls.user_author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user_author)
        cache.clear()

    def test_creating_post(self):
        """Проверка при создании поста."""
        pages_post = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for reverse_name in pages_post:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertEqual(
                    response.context['page_obj'][0].group.title, 'test_group'
                )

    def test_post_not_in_other_group(self):
        response = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug_1'}))
        self.assertNotIn(self.post, response.context['page_obj'])


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.post_follower = User.objects.create(
            username='post_follower',
        )
        cls.post = Post.objects.create(
            text='Текст для теста подписки',
            author=cls.post_author,
        )

    def setUp(self):
        cache.clear()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_follower)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_follow_on_user(self):
        """Проверка подписки на автора."""
        count_follow = Follow.objects.count()
        self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.post_follower}))
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author_id, self.post_follower.id)
        self.assertEqual(follow.user_id, self.post_author.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от автора."""
        Follow.objects.create(
            user=self.post_author,
            author=self.post_follower)
        count_follow = Follow.objects.count()
        self.authorized_client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.post_follower}))
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_follow_on_authors(self):
        """Проверка записей у тех кто подписан."""
        post = Post.objects.create(
            author=self.post_author,
            text='Текст для теста подписки')
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_author)
        response = self.authorized_author.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_notfollow_on_authors(self):
        """Проверка записей у тех кто не подписан на автора."""
        post = Post.objects.create(
            author=self.post_author,
            text='Текст для теста подписки')
        response = self.authorized_author.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
