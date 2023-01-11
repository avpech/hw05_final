from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.no_access_user = User.objects.create_user(username='outsider')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длиннее 15 символов',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.no_access_client = Client()
        self.no_access_client.force_login(self.no_access_user)

    def tearDown(self):
        cache.clear()

    def test_urls_exist(self):
        """URL-адрес доступен любому пользователю."""
        urls = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exist_authorized(self):
        """URL-адрес доступен авторизованному пользователю."""
        urls = [
            '/create/',
            f'/posts/{self.post.pk}/edit/',
            '/follow/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_to_login(self):
        """URL-адрес перенаправляет неавторизованного пользователя
        на страницу авторизации.
        """
        urls = [
            '/create/',
            f'/posts/{self.post.pk}/edit/',
            f'/posts/{self.post.pk}/comment/',
            f'/profile/{self.user.username}/follow/',
            f'/profile/{self.user.username}/unfollow/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_post_edit_url_redirect_authorised_without_access(self):
        """Перенаправление со страницы редактирования чужого поста
        на страницу с детальной информацией соответствующего поста
        для авторизованного пользователя.
        """
        url = f'/posts/{self.post.pk}/edit/'
        response = self.no_access_client.get(url, follow=True)
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates = {
            '/': 'posts/index.html',
            '/follow/': 'posts/follow.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unexisting_url_returns_404(self):
        """Несуществующий URL возвращает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
