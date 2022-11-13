from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersURLTests.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/logout/': 'users/logged_out.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_exists_at_desired_location(self):
        """Страница доступна любому авторизованному пользователю."""
        url_names = (
            '/auth/signup/', '/auth/login/',
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/reset/done/',
            '/auth/reset/uidb64/token/',
            '/auth/password_reset/done/',
            '/auth/logout/'
        )
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        url_names = (
            '/auth/signup/', '/auth/login/',
            '/auth/password_reset/',
            '/auth/reset/done/',
            '/auth/reset/uidb64/token/',
            '/auth/password_reset/done/',
            '/auth/logout/'
        )
        for address in url_names:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_url_redirect_anonymous(self):
        """Страницы /auth/password_change/ и
        /auth/password_change/done/ перенаправляет
        анонимного пользователя на страницу авторизации."""
        url_names = {
            '/auth/password_change/':
            '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
            '/auth/login/?next=/auth/password_change/done/'
        }
        for address, log in url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(response, log)
