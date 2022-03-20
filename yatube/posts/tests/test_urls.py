from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_one = User.objects.create_user(username='UserOne')
        cls.user_two = User.objects.create_user(username='UserTwo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст длинною больше 15 символов.',
            author=PostsURLTests.user_one,
            group=PostsURLTests.group,
        )
        cls.guest = Client()
        cls.logged1 = Client()
        cls.logged1.force_login(PostsURLTests.user_one)
        cls.logged2 = Client()
        cls.logged2.force_login(PostsURLTests.user_two)

    def test_urls_are_available_for_guest(self):
        """Проверка доступности страниц из списка
        неавторизованному пользователю."""
        urls_for_guest = [
            '/',
            '/group/testgroup/',
            f'/{PostsURLTests.user_one.username}/',
            f'/{PostsURLTests.user_one.username}/{PostsURLTests.post.id}/',
        ]
        for each_url in urls_for_guest:
            with self.subTest(each_url=each_url):
                response = PostsURLTests.guest.get(each_url)
                self.assertEqual(response.status_code, 200,
                                 f'проверьте {each_url}')

    def test_urls_use_correct_template_for_guest(self):
        """Проверка на правильность используемого шаблона
        для страниц из словаря, когда к ним обращается
        неавторизованный пользователь."""
        userpath = PostsURLTests.user_one.username
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/testgroup/',
            'profile.html': f'/{PostsURLTests.user_one.username}/',
            'post.html': f'/{userpath}/{PostsURLTests.post.id}/',
            'misc/404.html': '/404/',
            'misc/500.html': '/500/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = PostsURLTests.guest.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_for_authorized_are_available(self):
        """Проверка доступности страниц из
        списка авторизованному пользователю."""
        userpath = PostsURLTests.user_one.username
        urls_for_author = [
            '/new/',
            '/follow/',
            f'/{userpath}/{PostsURLTests.post.id}/edit/',
        ]
        for each_url in urls_for_author:
            with self.subTest(each_url=each_url):
                response = PostsURLTests.logged1.get(each_url)
                self.assertEqual(response.status_code, 200,
                                 f'проверьте {each_url}')

    def test_urls_use_correct_template_for_authorized(self):
        """Проверка на правильность используемого шаблона
        для страниц из словаря, когда к ним обращается
        авторизованный пользователь."""
        userpath = PostsURLTests.user_one.username
        templates_url_names = {
            '/new/': 'new.html',
            '/follow/': 'follow.html',
            f'/{userpath}/{PostsURLTests.post.id}/edit/': 'new.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = PostsURLTests.logged1.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_guest_correctly(self):
        """Проверяем для страниц из словаря, что неавторизованный
        пользователь переадресуется на нужную страницу."""
        userpath = PostsURLTests.user_one.username
        url_redirects = {
            '/auth/login/?next=/new/': '/new/',
            f'/auth/login/?next=/{userpath}/{PostsURLTests.post.id}/edit/':
                f'/{userpath}/{PostsURLTests.post.id}/edit/',
            f'/auth/login/?next=/{userpath}/{PostsURLTests.post.id}/comment':
                f'/{userpath}/{PostsURLTests.post.id}/comment',
            f'/auth/login/?next=/{userpath}/follow/':
                f'/{userpath}/follow/',
            f'/auth/login/?next=/{userpath}/unfollow/':
                f'/{userpath}/unfollow/',
        }
        for redir, address in url_redirects.items():
            with self.subTest(address=address):
                response = PostsURLTests.guest.get(address, follow=True)
                self.assertRedirects(response, redir)

    def test_urls_post_edit_redirects_athorized_nonauthor(self):
        """Проверяем для страницы /<username>/<post-id>/edit/,
        что авторизованный пользователь - не-автор
        переадресуется на нужную страницу."""
        userpath = PostsURLTests.user_one.username
        url_for_edit = f'/{userpath}/{PostsURLTests.post.id}/edit/'
        redir = f'/{userpath}/{PostsURLTests.post.id}/'
        response = PostsURLTests.logged2.get(
            url_for_edit, follow=True)
        self.assertRedirects(response, redir)

    def test_comments_and_follows_redirect_auth_correctly(self):
        userpath = PostsURLTests.user_one.username
        url_redirects = {
            f'/{userpath}/{PostsURLTests.post.id}/comment':
                f'/{userpath}/{PostsURLTests.post.id}/',
            f'/{userpath}/follow/': f'/{userpath}/',
            f'/{userpath}/unfollow/': f'/{userpath}/',
        }
        for address, redir in url_redirects.items():
            with self.subTest(address=address):
                response = PostsURLTests.logged1.get(address, follow=True)
                self.assertRedirects(response, redir)
