from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ('group', 'text', 'image')

        labels = {
            'group': ('Группа'),
            'text': ('Текст')
        }

        help_texts = {
            'group': ('Выберите группу для новой записи'),
            'text': ('Добавьте текст для новой записи')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text': ('Текст')
                  }
