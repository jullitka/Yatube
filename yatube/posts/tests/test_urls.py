from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый пост',
        )
        # Страницы доступны любому пользователю
        cls.PUBLIC_URLS = {
            '/': 'posts/index.html',
            '/group/Тестовый слаг/': 'posts/group_list.html',
            f'/profile/{cls.auth}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
        }
        # Страницы доступны любому авторизованному пользователю
        cls.AUTHORIZED_USER_URLS = {
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        # Страницы доступны только автору
        cls.AUTHORIZED_AUTHOR_URLS = {
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
        }
        # Перенаправляют на страницу авторизации
        cls.REDIRECT_FROM_PAGES = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{cls.post.id}/edit/':
            f'/auth/login/?next=/posts/{cls.post.id}/edit/',
        }
        # Перенаправляют НЕ автора на соответствующую страницу
        cls.REDIRECT_NOT_AUTHOR = {
            f'/posts/{cls.post.id}/edit/':
            f'/posts/{cls.post.id}/'
        }
        # Несуществующая страница
        cls.UNEXISTING_PAGE = '/unexisting_page/'

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.auth)
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        for address in self.PUBLIC_URLS.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_exists_at_desired_location(self):
        """Страница доступна  любому авторизованному пользователю."""
        for address in self.AUTHORIZED_USER_URLS.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_exists_at_desired_location(self):
        """Страница доступна  автору."""
        for address in self.AUTHORIZED_AUTHOR_URLS.keys():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_url_redirect_anonymous(self):
        """Страница, доступная авторизованному пользователю, перенаправляет
        анонимного пользователя на страницу авторизации."""
        for address, redirect in self.REDIRECT_FROM_PAGES.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(response, redirect)

    def test_edit_redirect_no_author(self):
        """Страница, доступная только автору, перенаправляет НЕ автора"""
        for address, redirect in self.REDIRECT_NOT_AUTHOR.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertRedirects(response, redirect)

    def test_unexisting_page_at_desired_location(self):
        """Несуществующая страница возвращает ошибку 404
        и использует кастомный шаблон."""
        response = self.client.get(self.UNEXISTING_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in {
            **self.PUBLIC_URLS,
            **self.AUTHORIZED_AUTHOR_URLS,
            **self.AUTHORIZED_USER_URLS
        }.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)
