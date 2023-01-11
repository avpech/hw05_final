import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='pic_1.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый тестовый пост',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data['text'],
                group=self.group,
                image='posts/pic_1.gif'
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост длиннее 15 символов',
            group=self.group
        )
        group = Group.objects.create(
            title='Тестовая группа номер 2',
            slug='test-slug-2',
            description='Тестовое описание номер 2',
        )
        posts_count = Post.objects.count()
        post_id = post.pk
        uploaded = SimpleUploadedFile(
            name='pic_2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный тестовый пост',
            'group': group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                pk=post_id,
                author=self.user,
                text=form_data['text'],
                group=group,
                image='posts/pic_2.gif'
            ).exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_create(self):
        """Валидная форма создает запись в Comment."""
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(self.post.comments.count(), comments_count + 1)
        self.assertTrue(
            self.post.comments.filter(
                author=self.user,
                post=self.post,
                text=form_data['text']
            )
        )
