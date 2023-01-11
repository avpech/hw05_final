from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длиннее 15 символов',
        )

    def test_post_model_have_correct_object_names(self):
        """Метод __str__ в объектах модели Post работает корректно."""
        post = self.post
        self.assertEqual(str(post), post.text[:15])

    def test_post_fields_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_fields_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = self.post
        field_help = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_group_model_have_correct_object_names(self):
        """Метод __str__ в объектах модели Group работает корректно."""
        group = self.group
        self.assertEqual(str(group), group.title)

    def test_group_fields_verbose_name(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Слаг',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длиннее 15 символов',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий'
        )

    def test_comment_model_have_correct_object_names(self):
        """Метод __str__ в объектах модели Comment работает корректно."""
        comment = self.comment
        self.assertEqual(str(comment), comment.text[:15])

    def test_comment_fields_verbose_name(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""
        comment = self.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'pub_date': 'Дата создания',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(user=cls.user, author=cls.author)

    def test_follow_model_have_correct_object_names(self):
        """Метод __str__ в объектах модели Follow работает корректно."""
        follow = self.follow
        expected = f'relation: {self.user.username} - {self.author.username}'
        self.assertEqual(str(follow), expected)

    def test_follow_fields_verbose_name(self):
        """verbose_name в полях модели Follow совпадает с ожидаемым."""
        follow = self.follow
        field_verboses = {
            'user': 'Пользователь',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name,
                    expected_value
                )
