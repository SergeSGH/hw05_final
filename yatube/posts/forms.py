from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'group',
            'text',
            'image'
        )
        help_texts = {
            'group': 'Введите группу для поста',
            'text': 'Текст поста',
            'image': 'Картинка поста'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Текст комментария',
        }
