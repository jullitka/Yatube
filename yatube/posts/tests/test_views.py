import shutil
import tempfile

from django.conf import settings
from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Новая тестовая группа',
            slug='Тестовый слаг новой группы',
            description='Тестовое описание новой группы'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Новый комментарий'
        )
        # Страницы, которые собирают группы постов
        cls.reverse_template_posts = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=[cls.auth]
            ): 'posts/profile.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        # страница поста
        cls.reverse_template_post_detail = {
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): 'posts/post_detail.html',
        }
        # страница создания поста
        cls.reverse_template_create = {
            reverse('posts:post_create'):
            'posts/create_post.html'
        }
        # редактировать пост
        cls.reverse_template_edit = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ): 'posts/create_post.html'
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        cls.reverse_name_group_2 = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group_2.slug}
        )
        cls.reverse_name_add_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id}
        )
        cls.reverse_index = reverse('posts:index')
        cls.reverse_follow_index = reverse('posts:follow_index')
        cls.reverse_profile_follow = reverse(
            'posts:profile_follow',
            args=[cls.auth]
        )
        cls.reverse_profile_unfollow = reverse(
            'posts:profile_unfollow',
            args=[cls.auth]
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.auth)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in {
            **self.reverse_template_posts,
            **self.reverse_template_create,
            **self.reverse_template_edit,
            **self.reverse_template_post_detail
        }.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            *self.reverse_template_create.keys()
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            *self.reverse_template_edit.keys()
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_show_correct_context(self):
        """Шаблон index, group_list, profile и follow_index
        сформированы с правильным контекстом."""
        # авторизованный пользователь подписался на автора поста
        self.authorized_client.get(self.reverse_profile_follow)
        for reverse_name in self.reverse_template_posts.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                self.assertEqual(
                    first_object.author,
                    self.post.author
                )
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(first_object.group, self.post.group)
                self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            *self.reverse_template_post_detail.keys()
        )
        self.assertEqual(
            response.context.get('post').text,
            self.post.text
        )
        self.assertEqual(
            response.context.get('post').author,
            self.auth
        )
        self.assertEqual(
            response.context.get('post').image,
            self.post.image
        )

    def test_post_added_to_page(self):
        """Пост при создании появляется
        на страницах index, group_list, profile
        и index_follow (при условии подписки на автора)"""
        # авторизованный пользователь подписался на автора поста
        self.authorized_client.get(self.reverse_profile_follow)
        for reverse_name in self.reverse_template_posts.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(
                    self.post,
                    response.context['page_obj'],
                    f'Поста почему-то нет на странице {reverse_name}'
                )

    def test_post_not_added_to_gtoup_2(self):
        """Созданный пост не попал в группу, для которой не был предназначен"""
        response = self.authorized_client.get(
            self.reverse_name_group_2
        )
        self.assertNotIn(
            self.post,
            response.context['page_obj'],
            'Пост есть в этой группе, а не должно быть!'
        )

    def test_comment_added_to_post_detail(self):
        """Комментарий появляется на странице поста, к которому он относится"""
        response = self.client.get(
            *self.reverse_template_post_detail.keys()
        )
        self.assertIn(
            self.comment,
            response.context['comments']
        )

    def test_cache(self):
        """Проверяет работу кеша"""
        response_1 = self.client.get(self.reverse_index)
        self.post_2 = Post.objects.create(
            author=self.auth,
            text='Тестовый пост 2',
            group=self.group,
        )
        response_2 = self.client.get(self.reverse_index)
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.client.get(self.reverse_index)
        self.assertNotEqual(response_1.content, response_3.content)

    def test_authorized_user_following_authors(self):
        """"Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок"""
        counter_following = Follow.objects.count()
        self.authorized_client.get(self.reverse_profile_follow)
        # количество подписок увеличелось на одну
        self.assertEqual(Follow.objects.count(), counter_following + 1)
        # подписка произошла на соответствующего автора
        self.assertTrue(Follow.objects.filter(
            author=self.auth,
            user=self.user
        ).exists())
        self.authorized_client.get(self.reverse_profile_unfollow)
        # количество подписок вернулось к исходному состоянию
        self.assertEqual(Follow.objects.count(), counter_following)
        # была удалена именно та подписка, которую удаляли
        self.assertFalse(Follow.objects.filter(
            author=self.auth,
            user=self.user
        ).exists())

    def test_post_not_added_to_profile_follow_not_follower(self):
        """Пост не добавляется в ленту тех, кто не подписан на его автора"""
        response = self.authorized_client.get(self.reverse_follow_index)
        self.assertNotIn(
            self.post,
            response.context['page_obj']
        )
