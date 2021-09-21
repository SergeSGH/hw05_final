from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post
from posts.tests.test_funcs import posts_create

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # создаем авторизованного пользователя
        cls.user = User.objects.create_user(username='VasyaPetrov')
        cls.posts_number = 15
        cls.group_post_number = 11

        # 15 постов 11 первой группы и 4 второй
        posts_create(
            cls, cls.posts_number, cls.group_post_number,
            'Тестовая группа', 'test_slug',
            'Тестовое описание', 'Тестовый пост')

        # создаем второго авторизованного пользователя
        cls.user2 = User.objects.create_user(username='PetyaVasechkin')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user2)

        # создаем третьего пользователя
        cls.user3 = User.objects.create_user(username='MashaStartseva')

        cls.test_new_post_text = 'Тестовый текст нового поста'

    def test_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={
                'username': self.user.username
            }))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertTrue(
            Follow.objects.filter(author=self.user).filter(
                user=self.user2
            ).exists()
        )

    def test_unfollow(self):
        """Авторизованный пользователь может удалять
            других пользователей из подписок"""
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={
                'username': self.user.username
            }))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        self.assertFalse(
            Follow.objects.filter(author=self.user).filter(
                user=self.user2
            ).exists()
        )

    def test_new_post(self):
        """Новая запись пользователя появляется в ленте тех, кто
        на него подписан и не появляется в ленте тех, кто не подписан"""

        # подписываем второго пользователя
        new_follow = Follow.objects.create(user=self.user2, author=self.user)
        new_follow.save()

        # создваем новую запись
        new_post = Post.objects.create(
            text=self.test_new_post_text,
            author=self.user,
            group=self.group
        )
        new_post.save()

        # проверяем, что запись есть в ленте подписанного пользователя
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            self.test_new_post_text,
            response.content.decode('utf-8')
        )

        # проверяем, что записи нет в ленте неподписанного пользователя
        self.authorized_client.force_login(self.user3)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            self.test_new_post_text,
            response.content.decode('utf-8')
        )
