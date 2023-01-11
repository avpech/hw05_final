from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersCreationFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Вася',
            'last_name': 'Иванов',
            'username': 'ivasya',
            'email': 'ivasya@pochta.com',
            'password1': 'qkjgs_dfj1_452',
            'password2': 'qkjgs_dfj1_452',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Вася',
                last_name='Иванов',
                username='ivasya',
                email='ivasya@pochta.com',
            ).exists()
        )
