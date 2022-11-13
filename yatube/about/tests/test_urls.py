from django.test import TestCase


class AboutURLTests(TestCase):
    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов статических страниц"""
        url_names = ('/about/author/', '/about/tech/')
        for url_name in url_names:
            with self.subTest(field=url_name):
                response = self.client.get(url_name)
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов статических страниц"""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
