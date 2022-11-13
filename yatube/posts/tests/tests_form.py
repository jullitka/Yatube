import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.models import Comment, Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Новая тестовая группа',
            slug='Тестовый слаг новой группы',
            description='Тестовое описание новой группы',
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.reverse_name_add_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id}
        )
        cls.comment_text = {
            'text': 'Новый комментарий'
        }
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
        cls.uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.form_data = {
            'text': 'Текст из формы',
            'group': cls.group.id,
            'image': cls.uploaded
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.auth)
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user,))
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        first_obj = Post.objects.first()
        self.assertEqual(first_obj.text, self.form_data['text'])
        self.assertEqual(first_obj.group.id, self.form_data['group'])
        self.assertEqual(first_obj.image.read(), self.small_gif)

    def test_edit_post(self):
        """Валидная форма изменяет пост в базе данных"""
        post_count = Post.objects.count()
        changed_form_data = {
            'text': 'Текст изменен',
            'group': self.group_2.id,
            'image': self.uploaded_2
        }
        response = self.authorized_author.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        ),
            data=changed_form_data,
            follow=True)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), post_count)
        first_obj = Post.objects.first()
        self.assertEqual(first_obj.text, changed_form_data['text'])
        self.assertEqual(first_obj.group.id, changed_form_data['group'])
        self.assertEqual(first_obj.image.read(), self.small_gif)

    def test_add_comment_only_authorithed_user(self):
        """Комментарий может добавлять авторизованный пользователь"""
        counter_posts = Comment.objects.count()
        self.authorized_client.post(
            self.reverse_name_add_comment,
            data=self.comment_text,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), counter_posts + 1)
        self.assertTrue(Comment.objects.filter(
            text=self.comment_text['text']
        ).exists())

    def test_not_add_comment_unauthorized_user(self):
        """Неавторизованный пользователь не может добавлять комментарий"""
        counter_posts = Comment.objects.count()
        self.client.post(
            self.reverse_name_add_comment,
            data=self.comment_text,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), counter_posts)
