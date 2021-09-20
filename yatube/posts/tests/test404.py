from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class Test404(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем авторизованного клиента
        cls.user = User.objects.create_user(username='VasyaPetrov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_test_404(self):
        """Тест, проверяющий, что страница 404 отдает кастомный шаблон"""

        response = self.authorized_client.get('any_url')
        self.assertTemplateUsed(response, 'core/404.html')
