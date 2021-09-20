from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание ',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длинный больше 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверка корректности работы метода __str__"""
        post = PostModelTest.post
        expected_post_name = post.text[:15]
        self.assertEqual(expected_post_name, str(post))

        group = PostModelTest.group
        expected_group_title = group.title
        self.assertEqual(expected_group_title, str(group))

    def test_verbose_name(self):
        """Проверка корректности verbose_name"""
        post = PostModelTest.post
        field_verboses = {
            'group': 'Группа',
            'author': 'Автор',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """Проверка корректности help_text"""
        post = PostModelTest.post
        field_help_text = {
            'group': 'Выберите группу',
            'author': 'Автор',
        }

        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
