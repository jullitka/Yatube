from django.core.cache import cache
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.NUM_POSTS_ON_PAGE_2 = 3
        cls.NUMBER_OF_POST = (
            settings.NUM_POSTS_ON_PAGE + cls.NUM_POSTS_ON_PAGE_2
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    author=cls.user,
                    text=num,
                    group=cls.group
                )
                for num in range(cls.NUMBER_OF_POST)
            ]
        )
        cls.reverse_names = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            reverse('posts:profile', args=[cls.user])
        )
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Проверка количества постов на первой странице"""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.NUM_POSTS_ON_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверка количества постов на первой странице"""
        for reverse_name in self.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(
                    response.context['page_obj']),
                    self.NUM_POSTS_ON_PAGE_2
                )
