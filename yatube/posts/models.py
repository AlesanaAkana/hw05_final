from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from yatube.constants import GROUP_STR_CUT_TITLE, POST_STR_CUT_TEXT

User = get_user_model()


class Post(CreatedModel):
    """Модель постов."""

    text = models.TextField(
        max_length=1000,
        verbose_name='Текст',
        help_text='Введите текст поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Сообщество',
        related_name='posts',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:POST_STR_CUT_TEXT]

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'post_id': self.pk})


class Group(models.Model):
    """Модель групп."""

    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Введите заголовок группы'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный адрес группы',
        unique=True
    )
    description = models.TextField(
        max_length=400,
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title[:GROUP_STR_CUT_TITLE]

    def get_absolute_url(self):
        return reverse('posts:group_list', kwargs={'slug': self.slug})


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        max_length=600,
        verbose_name='Комментарий',
        help_text='Введите комментарий поста'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'post_id': self.post.pk})


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
