from http import HTTPStatus

from django.test import Client, TestCase


class ViewTestClass(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_error_page(self):
        """Страница 404 отдает кастомный шаблон."""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
