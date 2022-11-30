from django import forms
from django.forms import Textarea

from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Группа не выбрана'

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст', 'group': 'Группа'}
        help_texts = {
            'text': 'Напишите текст вашего поста',
            'group': 'Выберите группу',
        }
        widgets = {
            'text': Textarea(attrs={'cols': 10, 'rows': 10,
                                    'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
