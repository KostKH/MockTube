import shutil

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post, User


class PostsViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=PostsViewsTests.small_gif,
            content_type='image/gif'
        )
        cls.gif_url = 'posts/small_1.gif'
        cls.user1 = User.objects.create_user(username='User1')
        cls.user2 = User.objects.create_user(username='User2')
        cls.user3 = User.objects.create_user(username='User3')
        cls.guest = Client()
        cls.logged1 = Client()
        cls.logged1.force_login(PostsViewsTests.user1)
        cls.logged2 = Client()
        cls.logged2.force_login(PostsViewsTests.user2)
        cls.logged3 = Client()
        cls.logged3.force_login(PostsViewsTests.user3)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Описание тестовой группы',
        )
        cls.group_two = Group.objects.create(
            title='Вторая тестовая группа',
            slug='testgroup2',
            description='Описание второй тестовой группы',
        )
        cls.post1 = Post.objects.create(
            text='Тестовый текст длинною больше 15 символов.',
            author=PostsViewsTests.user1,
            group=PostsViewsTests.group,
            image=PostsViewsTests.uploaded
        )
        cls.post2 = Post.objects.create(
            text='2-й пост длинною больше 15 символов.',
            author=PostsViewsTests.user2,
            group=PostsViewsTests.group,
            image=PostsViewsTests.uploaded
        )
        Follow.objects.create(
            author=PostsViewsTests.user1,
            user=PostsViewsTests.user3
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group_posts', args=[PostsViewsTests.group.slug])
            ),
            'new.html': reverse('new_post'),
            'post.html': (
                reverse('post', args=[
                    PostsViewsTests.user1.username,
                    PostsViewsTests.post1.id,
                ])
            ),
            'profile.html': (
                reverse('profile', args=[PostsViewsTests.user1.username])
            ),
            'follow.html': reverse('follow_index'),
            'misc/404.html': reverse('err404'),
            'misc/500.html': reverse('err500'),
        }
        for template, revers_name in templates_pages_names.items():
            with self.subTest(revers_name=revers_name):
                response = PostsViewsTests.logged1.get(revers_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        """В шаблон index передан правильный контекст."""
        response = PostsViewsTests.guest.get(reverse('index'))
        page = response.context.get('page')
        post_text = page[0].text
        post_author = page[0].author.username
        post_image = page[0].image
        expect_text = Post.objects.all().first().text
        expect_author = Post.objects.all().first().author.username
        expect_image = Post.objects.all().first().image
        self.assertEqual(post_text, expect_text)
        self.assertEqual(post_author, expect_author)
        self.assertEqual(post_image, expect_image)

    def test_group_shows_correct_context(self):
        """В шаблон group передан правильный контекст."""
        response = (
            PostsViewsTests.guest.get(
                reverse('group_posts', args=[PostsViewsTests.group.slug])
            )
        )
        group_title = response.context.get('group').title
        group_description = response.context.get('group').description
        page = response.context.get('page')
        post_text = page[0].text
        post_author = page[0].author.username
        post_image = page[0].image
        expect_post = Post.objects.filter(group=PostsViewsTests.group).first()
        expect_text = expect_post.text
        expect_author = expect_post.author.username
        expect_image = expect_post.image
        self.assertEqual(group_title, PostsViewsTests.group.title)
        self.assertEqual(group_description, PostsViewsTests.group.description)
        self.assertEqual(post_text, expect_text)
        self.assertEqual(post_author, expect_author)
        self.assertEqual(post_image, expect_image)

    def test_profile_shows_correct_context(self):
        """В шаблон profile передан правильный контекст."""
        response = (
            PostsViewsTests.guest.get(
                reverse('profile', args=[PostsViewsTests.user1.username])
            )
        )
        author = response.context.get('author').username
        author_fullname = response.context.get('author').get_full_name
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author.username
        post_image = response.context.get('page')[0].image
        post_following = response.context.get('following')
        expect_author = PostsViewsTests.user1.username
        expect_fullname = PostsViewsTests.user1.get_full_name
        expect_post = PostsViewsTests.user1.posts.all().first()
        self.assertEqual(author, expect_author)
        self.assertEqual(author_fullname, expect_fullname)
        self.assertEqual(post_text, expect_post.text)
        self.assertEqual(post_author, expect_post.author.username)
        self.assertEqual(post_image, expect_post.image)
        self.assertFalse(post_following)

    def test_post_template_shows_correct_context(self):
        """В шаблон post передан правильный контекст."""
        response = (
            PostsViewsTests.guest.get(
                reverse('post', args=[PostsViewsTests.user1.username,
                        PostsViewsTests.post1.id])
            )
        )
        author = response.context.get('author').username
        author_fullname = response.context.get('author').get_full_name
        post_text = response.context.get('post').text
        post_author = response.context.get('post').author.username
        post_image = response.context.get('post').image
        post_following = response.context.get('following')
        self.assertEqual(author, PostsViewsTests.user1.username)
        self.assertEqual(
            author_fullname,
            PostsViewsTests.user1.get_full_name,
        )
        self.assertEqual(post_text, PostsViewsTests.post1.text)
        self.assertEqual(post_author, PostsViewsTests.user1.username)
        self.assertEqual(post_image, PostsViewsTests.gif_url)
        self.assertEqual(post_image, PostsViewsTests.gif_url)
        self.assertFalse(post_following)

    def test_newpost_template_show_correct_context_index(self):
        """В шаблон для создания поста передан правильный контекст."""
        response = PostsViewsTests.logged1.get(reverse('new_post'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (
            PostsViewsTests.logged1.get(
                reverse('post_edit', args=[PostsViewsTests.user1.username,
                                           PostsViewsTests.post1.id])
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_is_shown_correctly(self):
        """Созданный пост выводится на главной странице."""
        check_post = PostsViewsTests.post1
        response = PostsViewsTests.guest.get(reverse('index'))
        post_list = response.context.get('page').object_list
        self.assertIn(check_post, post_list)

    def test_post_is_shown_correctly(self):
        """Созданный пост выводится на странице своей группы."""
        check_post = PostsViewsTests.post1
        response = (
            PostsViewsTests.guest.get(
                reverse('group_posts', args=[PostsViewsTests.group.slug])
            )
        )
        post_list = response.context.get('page').object_list
        self.assertIn(check_post, post_list)

    def test_post_is_shown_correctly(self):
        """Созданный пост не выводится на странице чужой группы."""
        check_post = PostsViewsTests.post1
        response = (
            PostsViewsTests.guest.get(
                reverse('group_posts', args=[PostsViewsTests.group_two.slug])
            )
        )
        post_list = response.context.get('page').object_list
        self.assertNotIn(check_post, post_list)

    def test_post_index_cache_works(self):
        """Проверяем работу кэша"""
        cache.clear()
        post = Post.objects.create(
            text='Тестируем кэш.',
            author=PostsViewsTests.user1,
            group=PostsViewsTests.group,
        )
        response1 = str(
            PostsViewsTests.guest.get(reverse('index')).content
        )
        post.delete()
        response2 = str(
            PostsViewsTests.guest.get(reverse('index')).content
        )
        self.assertHTMLEqual(response1, response2)
        cache.clear()
        response3 = str(
            PostsViewsTests.guest.get(reverse('index')).content
        )
        self.assertHTMLNotEqual(response1, response3)

    def test_post_visible_to_followers(self):
        """Пост виден подписанным пользователям в ленте подписок."""
        follower = PostsViewsTests.logged3
        post_to_see = PostsViewsTests.post1
        response = follower.get(reverse('follow_index'))
        post_list = response.context.get('page').object_list
        self.assertIn(post_to_see, post_list)

    def test_post_not_visible_to_non_followers(self):
        """Пост не виден неподписанным пользователям в ленте подписок."""
        non_follower = PostsViewsTests.logged2
        post_to_see = PostsViewsTests.post1
        response = non_follower.get(reverse('follow_index'))
        post_list = response.context.get('page').object_list
        self.assertNotIn(post_to_see, post_list)

    def test_logged_user_can_follow_author(self):
        """Пользователь может подписаться на автора"""
        client = PostsViewsTests.logged1
        user = PostsViewsTests.user1
        author = PostsViewsTests.user2
        client.get(reverse('profile_follow', args=[author.username]))
        expected = Follow.objects.filter(user=user, author=author).exists()
        self.assertTrue(expected)

    def test_logged_user_can_unfollow_author(self):
        """Пользователь может отписаться от автора"""
        client = PostsViewsTests.logged1
        user = PostsViewsTests.user1
        author = PostsViewsTests.user2
        if not Follow.objects.filter(user=user, author=author).exists():
            Follow.objects.create(user=user, author=author)
        client.get(reverse('profile_unfollow', args=[author.username]))
        expected = Follow.objects.filter(user=user, author=author).exists()
        self.assertFalse(expected)


class PaginatorViewsTest(TestCase):
    number_on_page = 10
    post_number = 13
    rest = post_number - number_on_page

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='User1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Описание тестовой группы',
        )
        Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовое сообщение{i}',
                    author=PaginatorViewsTest.user1,
                    group=PaginatorViewsTest.group,
                )
                for i in range(PaginatorViewsTest.post_number)
            ]
        )
        cls.guest = Client()

    def test_first_page_has_correct_number_of_posts(self):
        """На первую страницу выводится заданное число постов."""
        reverses = [
            reverse('index'),
            reverse('group_posts', args=[PaginatorViewsTest.group.slug]),
            reverse('profile', args=[PaginatorViewsTest.user1.username]),
        ]
        for reverse_name in reverses:
            with self.subTest(reverse_name=reverse_name):
                response = PaginatorViewsTest.guest.get(reverse_name)
                number_to_check = (
                    len(response.context.get('page').object_list)
                )
                expected = PaginatorViewsTest.number_on_page
                self.assertEqual(number_to_check, expected)

    def test_index_second_page_has_correct_number_of_posts(self):
        """На 2-ю страницу выводится корректный остаток постов."""
        reverses = [
            reverse('index'),
            reverse('group_posts', args=[PaginatorViewsTest.group.slug]),
            reverse('profile', args=[PaginatorViewsTest.user1.username]),
        ]
        for rev_name in reverses:
            with self.subTest(rev_name=rev_name):
                response = (
                    PaginatorViewsTest.guest.get(rev_name + '?page=2')
                )
                number_to_check = (
                    len(response.context.get('page').object_list)
                )
                expected = PaginatorViewsTest.rest
                self.assertEqual(number_to_check, expected)
