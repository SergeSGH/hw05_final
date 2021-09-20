import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post
from posts.tests.test_funcs import posts_create

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImagePostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # создание авторизованного клиента
        cls.user = User.objects.create_user(username='VasyaPetrov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # создание 15 постов в 2х группах
        posts_create(
            cls, 15, 11, 'Тестовая группа', 'test_slug',
            'Тестовое описание', 'Тестовый пост')

        cls.test_image_name = 'test_image.gif'
        test_gif_bytes = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B")
        cls.uploaded_image = SimpleUploadedFile(
            name=cls.test_image_name,
            content=test_gif_bytes,
            content_type='image/gif')

        cls.test_new_post_text = 'Тестовый текст нового поста'

        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_image_in_post(self):
        """Проверяем, что при отправке поста с картинкой
        через форму PostForm создаётся запись в базе данных"""
        posts_count = Post.objects.count()

        # пост
        form_data = {
            'text': self.test_new_post_text,
            'group': self.group.id,
            'image': self.uploaded_image
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # проверяем переадресацию на страницу профиля
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username
        }))

        # проверяем что число постов увеличилось на 1
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # в последнем по id посте есть группа, картинка и текст
        posts = Post.objects.all().order_by('id')
        last_post = posts[len(posts) - 1]
        self.assertEqual(
            last_post.text, self.test_new_post_text
        )
        self.assertEqual(
            last_post.group, self.group
        )
        self.assertIn(self.test_image_name, str(last_post.image))

    def test_post_image_in_context(self):
        """Проверка корректности отображения поста на странице поста"""

        new_post = Post.objects.create(
            text=self.test_new_post_text,
            author=self.user,
            group=self.group,
            image=self.uploaded_image
        )

        posts = Post.objects.all().order_by('id')
        last_post = posts[len(posts) - 1]
        self.assertEqual(new_post, last_post)

        # проверка контекста для страниц со списком постов
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        ]

        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.text, self.test_new_post_text)
                self.assertEqual(post.author.username, self.user.username)
                self.assertEqual(post.group.title, self.group.title)
                self.assertIn(
                    self.test_image_name[:len(self.test_image_name)-4],
                    str(post.image)
                )

        # проверка контекста для страницы поста
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': last_post.id}
        )))
        self.assertEqual(
            response.context.get('post').author.username, self.user.username
        )
        self.assertEqual(
            response.context.get('post').text, self.test_new_post_text
        )
        self.assertEqual(
            response.context.get('post').group,
            self.group
        )
        self.assertIn(
            self.test_image_name[:len(self.test_image_name)-4],
            str(response.context.get('post').image)
        )
