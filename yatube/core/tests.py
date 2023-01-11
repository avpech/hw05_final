from http import HTTPStatus

from django.test import Client, TestCase


class CoreViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_nonexist_url_correct(self):
        """Страница ошибки 404 отображается корректно."""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
