from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.tests.test_funcs import posts_create

User = get_user_model()


class PostViewsTests(TestCase):
    """Проверка вью-классов"""
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
            text='Тестовый пост длинный больше 15 символов',
        )
        cls.test_post_id = cls.post.id
        cls.test_post_text = cls.post.text
        cls.test_post_group_title = cls.group.title
        cls.test_slug = cls.group.slug

    def test_post_pages_use_correct_templates(self):
        """ Проверка корректности шаблонов """

        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_posts', kwargs={'slug': self.test_slug})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={
                    'username': self.user.username
                })
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={
                    'post_id': self.test_post_id
                })
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={
                    'post_id': self.test_post_id
                })
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_static_pages_use_correct_templates(self):
        """Проверка корректности шаблонов для статичных страниц"""
        response = self.client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

        response = self.client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')

    def test_static_pages_accessible_by_name(self):
        """Проверка что статические страницы доступны по имени"""
        pages_names = [
            reverse('about:author'),
            reverse('about:tech')
        ]

        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class PostContextTests(TestCase):
    """Проверка что view-классы используют корректный контекст"""
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

        cls.test_post_id = cls.post.id
        cls.test_post_text = cls.post.text
        cls.test_post_group_title = cls.group.title
        cls.test_post_slug = cls.group.slug

        cls.test_first_group_title = 'Тестовая группа1'
        cls.test_first_slug = 'test_slug1'
        cls.test_first_group_id = Group.objects.get(
            slug=cls.test_first_slug
        ).id

    def test_index_use_correct_context(self):
        """Проверка контекста для главной страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        elements_num = len(page_obj)

        # проверяем что количество постов на странице равно
        # числу постов паджинатора
        self.assertEqual(elements_num, settings.POSTS_NUMBER)

        # проверяем что каждый элемент это пост
        for post in page_obj:
            self.assertIsInstance(post, Post)

        # проверяем что посты отсортированы по дате
        page_obj_list = page_obj.object_list
        page_obj_list_dict = [
            {'pub_date': post.pub_date, 'post': post}
            for post in page_obj_list
        ]
        page_obj_list_dict_unsort = page_obj_list_dict
        page_obj_list_dict.sort(key=lambda k: k['pub_date'], reverse=True)
        self.assertEqual(page_obj_list_dict, page_obj_list_dict_unsort)

    def test_group_list_uses_correct_context(self):
        """Проверка контекста для страницы группы"""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.test_first_slug})
        )
        page_obj = response.context.get('page_obj')
        elements_num = len(page_obj)

        # проверяем что количество постов на странице равно
        # числу постов паджинатора
        self.assertEqual(elements_num, settings.POSTS_NUMBER)

        # проверяем что каждый элемент это пост заданной группы
        for post in page_obj:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.group.title, self.test_first_group_title)
            self.assertEqual(post.group.id, self.test_first_group_id)

    def test_profile_uses_correct_context(self):
        """Проверка контекста для страницы пользователя"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        page_obj = response.context.get('page_obj')
        elements_num = len(page_obj)

        # проверяем что количество постов на странице равно 10
        self.assertEqual(elements_num, settings.POSTS_NUMBER)

        # проверяем что каждый элемент это пост заданного пользователя
        for post in page_obj:
            self.assertIsInstance(post, Post)
            self.assertEqual(post.author.username, self.user.username)

    def test_index_second_page(self):
        """Допроверка паджинатора для главной страницы"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj']),
            self.posts_number - settings.POSTS_NUMBER
        )

    def test_profile_second_page(self):
        """Допроверка паджинатора для страницы профиля"""
        response = self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            self.posts_number - settings.POSTS_NUMBER
        )

    def test_group_second_page(self):
        """Допроверка паджинатора для страницы группы"""
        response = self.client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': 'test_slug1'}
        ) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            self.group_post_number - settings.POSTS_NUMBER
        )

    def test_post_edit(self):
        """Допроверка классов полей форм для страницы редактирования поста"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.test_post_id}
        ))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_create_post(self):
        """Допроверка классов полей форм для страницы создания поста"""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_post(self):
        """Проверка корректности отображения поста на странице поста"""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.test_post_id}
        )))
        self.assertEqual(
            response.context.get('post').author.username, self.user.username
        )
        self.assertEqual(
            response.context.get('post').text, self.test_post_text
        )
        self.assertEqual(
            response.context.get('post').group.title,
            self.test_post_group_title
        )

    def test_one_post_correct_context(self):
        """Проверка корректности отображения поста с группой на 3х страницах"""
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.test_post_slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]

        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.text, self.test_post_text)
                self.assertEqual(post.author.username, self.user.username)
                self.assertEqual(post.group.title, self.test_post_group_title)

    def test_one_post_not_in_incorrect_gr(self):
        """Проверка что пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.test_first_slug})
        )
        page_obj = response.context['page_obj']
        for post in page_obj:
            self.assertNotEqual(post.text, self.test_post_text)
