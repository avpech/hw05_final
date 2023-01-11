from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist(self):
        """URL-адрес доступен любому пользователю."""
        urls = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unexisting_url_returns_404(self):
        """Несуществующий URL возвращает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class AboutPagesTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_use_cirrect_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
