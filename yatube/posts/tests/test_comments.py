from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, Comment

User = get_user_model()


class CommentsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # создание авторизованного клиента, группы и поста
        cls.user = User.objects.create_user(username='VasyaPetrov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длинной больше 15 символов',
            group=cls.group
        )
        cls.ex_comment = Comment.objects.create(
            author=cls.user,
            text='Первый коммент поста',
            post=cls.post
        )
        cls.new_comment_text = 'Тестовый комментарий поста'

    def test_comment_creation(self):
        """Проверяем, что при добавлении комментария
        авторизованым пользователем от сохраняется и
        показывается на странице"""
        comments_count = self.post.comments.count()

        # комментарий
        comment_data = {
            'text': self.new_comment_text
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.id
            }),
            data=comment_data,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # проверяем что число комментариев увеличилось на 1
        self.assertEqual(self.post.comments.count(), comments_count + 1)

        # последний по id коммент относится к нужному посту
        # с тестовым текстом
        comments = self.post.comments.all().order_by('id')
        last_comment = comments[len(comments) - 1]
        self.assertEqual(
            last_comment.text, self.new_comment_text
        )
        self.assertEqual(
            last_comment.post, self.post
        )

    def test_comment_creation_anonim(self):
        """Проверяем, что при добавлении комментария
        анонимом он не сохраняется и
        показывается на странице"""
        comments_count = self.post.comments.count()

        # комментарий
        comment_data = {
            'text': self.new_comment_text
        }
        response = self.client.post(
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            }),
            data=comment_data,
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # проверяем что число комментариев не увеличилось
        self.assertEqual(self.post.comments.count(), comments_count)

        # провераем что среди комметариев нет нового
        self.assertFalse(
            Comment.objects.filter(text=self.new_comment_text).exists()
        )
