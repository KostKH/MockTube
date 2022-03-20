from django.test import Client, TestCase


class StaticURLTest(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемые при помощи имен статичных страниц, доступны."""
        addresses = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)
