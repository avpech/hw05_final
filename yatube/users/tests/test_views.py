from typing import Dict

from django import forms
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def _check_form(self,
                    form_fields: Dict[str, forms.Field],
                    response: HttpResponse
                    ):
        """Проверить поля формы на соответствие ожидаемым типам."""
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(form_field, expected)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': '<uidb64>', 'token': '<token>'}
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        response = self.guest_client.get(reverse('users:signup'))
        self._check_form(form_fields=form_fields, response=response)

    def test_login_show_correct_context(self):
        """Шаблон login сформирован с правильным контекстом."""
        form_fields = {
            'username': forms.fields.CharField,
            'password': forms.fields.CharField,
        }
        response = self.guest_client.get(reverse('users:login'))
        self._check_form(form_fields=form_fields, response=response)

    def test_password_change_show_correct_context(self):
        """Шаблон password_change сформирован с правильным контекстом."""
        form_fields = {
            'old_password': forms.fields.CharField,
            'new_password1': forms.fields.CharField,
            'new_password2': forms.fields.CharField,
        }
        response = self.authorized_client.get(
            reverse('users:password_change')
        )
        self._check_form(form_fields=form_fields, response=response)

    def test_pasword_reset_show_correct_context(self):
        """Шаблон password_reset_form сформирован с правильным контекстом."""
        form_fields = {
            'email': forms.fields.EmailField,
        }
        response = self.guest_client.get(reverse('users:password_reset_form'))
        self._check_form(form_fields=form_fields, response=response)
