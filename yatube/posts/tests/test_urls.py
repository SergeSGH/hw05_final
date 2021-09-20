from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):

    def test_author_tech_homepage(self):
        """Функция проверяет доступность адресов для статичных страниц"""
        url_list = [
            '/about/author/',
            '/about/tech/',
            '/'
        ]

        for url in url_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем авторизованного клиента
        cls.user = User.objects.create_user(username='VasyaPetrov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создаем тестовую группу и пост
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длинный больше 15 символов',
        )
        cls.slug = cls.group.slug

    def test_post_pages_accessible_by_name1(self):
        """ Проверка что страницы постов доступны по имени
            для авторизованного пользователя """
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.slug}),
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }),
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id
            }),
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            })
        ]

        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_pages_accessible_by_name2(self):
        """ Проверка что страницы постов доступны по имени
            для неавторизованного пользователя """
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.slug}),
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }),
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            })
        ]

        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_url_exists_at_desired_location(self):
        """Проверка доступности главной страницы для любого пользователя"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_posts_exists_at_desired_location(self):
        """Проверка доступности страницы группы для любого пользователя"""
        group = PostURLTests.group
        group_slug = group.slug
        response = self.client.get(
            '/group/' + group_slug + '/',
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_username_exists_at_desired_location(self):
        """ Проверка доступности страницы авторизованного пользователя для
            любого пользователя """
        user = PostURLTests.user
        username = user.username
        response = self.client.get(
            '/profile/' + username + '/', follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_postid_exists_at_desired_location(self):
        """ Проверка доступности страницы поста для любого пользователя """
        id = PostURLTests.post.id
        response = self.client.get('/posts/' + str(id) + '/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_exists_at_desired_location(self):
        """ Проверка доступности страницы по созданию поста для авторизованного
            пользователя """
        response = PostURLTests.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_postid_edit_at_desired_location(self):
        """ Проверка доступности страницы по редактированию поста для
            авторизованного пользователя """
        id = PostURLTests.post.id
        response = PostURLTests.authorized_client.get(
            '/posts/' + str(id) + '/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_any_page_404(self):
        """Проверка запроса к несуществующей странице"""
        response = PostURLTests.authorized_client.get('/any_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_redirect_anonymous_on_admin_login(self):
        """ Проверка редиректа со страницы по созданию поста для
            неавторизованного пользователя """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_post_edit_on_another_login(self):
        """ Проверка редиректа со страницы по созданию поста для
        другого пользователя """
        id = PostURLTests.post.id
        self.user = User.objects.create_user(username='IvanSidorov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get('/posts/' + str(id) + '/edit/')
        self.assertRedirects(
            response, ('/posts/' + str(id) + '/'))

    def test_urls_uses_correct_template(self):
        """ Проверка вызываемых шаблонов для каждого адреса """
        id = PostURLTests.post.id
        post_url = '/posts/' + str(id) + '/'
        post_url_edit = '/posts/' + str(id) + '/edit/'
        templates_url_names = {
            'posts/index.html': '/',
            'posts/create_post.html': '/create/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': '/profile/VasyaPetrov/',
            'posts/post_detail.html': post_url,
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

        response = self.authorized_client.get(post_url_edit)
        self.assertTemplateUsed(response, 'posts/create_post.html')
