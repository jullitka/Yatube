from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UsersFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',

        }

    # def test_signup_(self):
    #   """При заполнении формы signup создается новый пользователь"""
    #    user_count = User.objects.count()
    #    self.assertEqual(response.status_code, 200)
    #    self.assertEqual(User.objects.count(), user_count + 1)
