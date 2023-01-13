import shutil
import tempfile
from typing import Dict

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        cache.clear()

    def _compare_post_fields(self, post: Post):
        """Сравнить поля полученного и тестового экземпляров Post."""
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def _compare_comment_fields(self, comment: Comment):
        """Сравнить поля полученного и тестового экземпляров Comment."""
        self.assertEqual(comment.author, self.comment.author)
        self.assertEqual(comment.text, self.comment.text)
        self.assertEqual(comment.post, self.comment.post)

    def _check_form_fields(self,
                           fields_expected: Dict[str, forms.Field],
                           response: HttpResponse
                           ):
        """Проверить поля формы на соответствие ожидаемым типам."""
        for field, expected in fields_expected.items():
            with self.subTest(field=field):
                form_field = response.context.get(
                    'form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self._compare_post_fields(post=first_post)

    def test_group_post_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        ))
        first_post = response.context['page_obj'][0]
        group = response.context['group']
        self._compare_post_fields(post=first_post)
        self.assertEqual(group, self.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        first_post = response.context['page_obj'][0]
        user_obj = response.context['user_obj']
        self._compare_post_fields(post=first_post)
        self.assertEqual(user_obj, self.user)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
        }
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        post = response.context['post']
        comment = response.context['comments'][0]
        author_posts_count = response.context['posts_count']
        self._compare_post_fields(post=post)
        self._compare_comment_fields(comment=comment)
        self.assertEqual(author_posts_count, post.author.posts.all().count())
        self._check_form_fields(
            fields_expected=form_fields,
            response=response
        )

    def test_follow_index_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""
        user = User.objects.create_user(username='follower')
        Follow.objects.create(user=user, author=self.user)
        follower_client = Client()
        follower_client.force_login(user)
        response = follower_client.get(reverse('posts:follow_index'))
        first_post = response.context['page_obj'][0]
        self._compare_post_fields(post=first_post)

    def test_unfollower_see_no_post(self):
        """Неподписанный пользователь не видит пост автора в избранном."""
        user = User.objects.create_user(username='unfollower')
        unfollower_client = Client()
        unfollower_client.force_login(user)
        response = unfollower_client.get(reverse('posts:follow_index'))
        page_obj = response.context['page_obj']
        self.assertNotIn(self.post, page_obj)

    def test_post_is_not_in_unexpected_group(self):
        """Пост не отображается в неподходящей группе."""
        group = Group.objects.create(
            title='Тестовая группа номер 2',
            slug='test-slug-2',
            description='Тестовое описание 2-й группы',
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': group.slug}
        ))
        page_obj = response.context['page_obj']
        self.assertNotIn(self.post, page_obj)

    def test_create_post_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.get(reverse('posts:post_create'))
        self._check_form_fields(
            fields_expected=form_fields,
            response=response
        )

    def test_edit_post_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        ))
        is_edit = response.context['is_edit']
        self._check_form_fields(
            fields_expected=form_fields,
            response=response
        )
        self.assertTrue(is_edit)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        posts_quantity = 23
        cls.posts = []
        for post_number in range(posts_quantity):
            post = Post.objects.create(
                author=cls.user,
                text=f'Пост номер {post_number}',
                group=cls.group
            )
            cls.posts.append(post)
        cls.pages = posts_quantity // settings.POSTS_ON_PAGE + 1

    def setUp(self):
        self.guest_client = Client()

    def _get_expected_posts_count(self,
                                  page_number: int
                                  ):
        """Получить ожидаемое количество постов на странице."""
        posts_count = (
            len(self.posts) - settings.POSTS_ON_PAGE * (page_number - 1)
        )
        if posts_count > settings.POSTS_ON_PAGE:
            posts_count = settings.POSTS_ON_PAGE
        return posts_count

    def test_home_page_correct_posts_count_on_page(self):
        """В шаблоне index отображается верное количество постов."""
        for page_number in range(1, self.pages + 1):
            with self.subTest(page=page_number):
                posts_count = self._get_expected_posts_count(page_number)
                response = self.guest_client.get(
                    reverse('posts:index') + f'?page={page_number}'
                )
                self.assertEqual(
                    len(response.context['page_obj']), posts_count
                )

    def test_group_list_correct_posts_count_on_page(self):
        """В шаблоне group_list отображается верное количество постов."""
        for page_number in range(1, self.pages + 1):
            with self.subTest(page=page_number):
                posts_count = self._get_expected_posts_count(page_number)
                response = self.guest_client.get(
                    reverse(
                        'posts:group_list',
                        kwargs={'slug': self.group.slug}
                    ) + f'?page={page_number}'
                )
                self.assertEqual(
                    len(response.context['page_obj']), posts_count
                )

    def test_profile_correct_posts_count_on_page(self):
        """В шаблоне profile отображается верное количество постов."""
        for page_number in range(1, self.pages + 1):
            with self.subTest(page=page_number):
                posts_count = self._get_expected_posts_count(page_number)
                response = self.guest_client.get(
                    reverse(
                        'posts:profile',
                        kwargs={'username': self.user.username}
                    ) + f'?page={page_number}'
                )
                self.assertEqual(
                    len(response.context['page_obj']), posts_count
                )


class CachePagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

    def tearDown(self):
        cache.clear()

    def test_home_page_cache(self):
        """Проверка кэширования шаблона index."""
        response = self.authorized_client.get(reverse('posts:index'))
        content = response.content

        self.post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_content = response.content
        self.assertEqual(cache_content, content)

        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        new_content = response.content
        self.assertNotEqual(new_content, cache_content)


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='user')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow(self):
        """Авторизованный пользователь может подписываться на автора."""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )

    def test_unfollow(self):
        """Авторизованный пользователь может удалять автора из подписок."""
        Follow.objects.create(user=self.user, author=self.author)
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author
            ).exists()
        )

    def test_self_following_forbidden(self):
        """Пользователь не может подписываться на себя."""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user
            ).exists()
        )
