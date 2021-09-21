from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post
from posts.tests.test_funcs import posts_create

User = get_user_model()


class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # создание авторизованного клиента
        cls.user = User.objects.create_user(username='VasyaPetrov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        posts_create(
            cls, 15, 11, 'Тестовая группа', 'test_slug',
            'Тестовое описание', 'Тестовый пост')

        cls.test_post_id = cls.post.id
        cls.test_post_text = cls.post.text
        cls.test_post_group_title = cls.group.title
        cls.test_post_slug = cls.group.slug

        cls.test_new_post_text = 'Тестовый текст нового поста'

        cls.form = PostForm()

    def test_create_post(self):
        """Тестирование создания поста"""
        posts_count = Post.objects.count()

        # пост
        form_data = {
            'text': self.test_new_post_text,
            'group': self.group.id,
        }

        # отправка пост-запроса для авторизованного пользователя
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=False
        )

        # проверяем, сработал ли редирект на страницу пользователя
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username
        }))

        # проверяем что число постов увеличилось на 1
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # сортируем список id постов и выбираем последний id
        last_post = Post.objects.all().order_by('-id').first()

        # проверяем что создался пост тестовой группы
        self.assertEqual(
            last_post.text, self.test_new_post_text
        )
        self.assertEqual(
            last_post.group, self.group
        )

    def test_create_post_anonim(self):
        """Тестирование создания поста анонимным пользователем"""
        # пост
        form_data = {
            'text': self.test_new_post_text,
            'group': self.group.id,
        }

        # создание поста под анонимом / редирект на страницу авторизации
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=False)
        self.assertIn(reverse('users:login'), response.url)

    def test_edit_post(self):
        """Тестирование редактирования поста"""
        posts_count = Post.objects.count()

        form_data = {
            'text': self.test_new_post_text,
            'group': self.group.id,
        }

        # отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.test_post_id}),
            data=form_data,
            follow=True
        )

        # проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.test_post_id
        }))

        # проверяем, не увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)

        # проверяем, что создалась запись с заданной группой
        self.assertEqual(
            Post.objects.get(id=self.test_post_id).text,
            self.test_new_post_text
        )
        self.assertEqual(
            Post.objects.get(id=self.test_post_id).group, self.group
        )

    def test_edit_post_anonim(self):
        """Тестирование редактирования поста анонимным пользователем"""

        form_data = {
            'text': self.test_new_post_text,
            'group': self.group.id,
        }

        # редактирование поста под анонимом / редирект на страницу авторизации
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.test_post_id}),
            data=form_data,
            follow=False
        )
        self.assertIn(reverse('users:login'), response.url)
