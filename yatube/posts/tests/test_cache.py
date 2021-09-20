import unittest

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post
from posts.tests.test_funcs import posts_create

User = get_user_model()


class CacheTest(TestCase):
    """Проверка кэширования индексной страницы"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # создаем авторизованного пользователя
        cls.user = User.objects.create_user(username='VasyaPetrov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.posts_number = 15
        cls.group_post_number = 11

        # 15 постов 11 первой группы и 4 второй
        posts_create(
            cls, cls.posts_number, cls.group_post_number,
            'Тестовая группа', 'test_slug',
            'Тестовое описание', 'Тестовый пост')

        cls.new_first_post_text = 'Обновленный пост'

    @unittest.skip
    def test_cache_for_index(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_post_text = str(response.context['page_obj'][0].text)
        first_post_id = response.context['page_obj'][0].id

        # проверяем наличие поста на главной странице
        self.assertIn(first_post_text, response.content.decode('utf-8'))

        # удаляем пост
        first_post = Post.objects.get(pk=first_post_id)
        first_post.delete()

        # пост остался на главной странице
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(first_post_text, response.content.decode('utf-8'))

        cache.clear()

        # поста нет на главной странице после очиски кэша
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(first_post_text, response.content.decode('utf-8'))
