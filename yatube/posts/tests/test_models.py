from django.test import TestCase

from yatube.constants import POST_STR_CUT_TEXT

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст больше 15 символов...пыщ-пыщ!',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:POST_STR_CUT_TEXT]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Уникальный адрес группы',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Введите заголовок группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для комментариев.',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Это тестовый коментарий!',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'text': 'Комментарий',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_help_texts = {
            'text': 'Введите комментарий поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        follow = FollowModelTest.follow
        expected_object_name = f'{self.user} подписан на {self.author}'
        self.assertEqual(expected_object_name, str(follow))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)
