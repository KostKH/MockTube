import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User


class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user1 = User.objects.create_user(username='UserOne')
        cls.user2 = User.objects.create_user(username='UserTwo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст длинною больше 15 символов.',
            author=PostsFormTests.user1,
            group=PostsFormTests.group,
        )
        cls.comm1 = Comment.objects.create(
            text='комментарий 1',
            author=PostsFormTests.user2,
            post=PostsFormTests.post

        )
        cls.logged1 = Client()
        cls.logged1.force_login(PostsFormTests.user1)
        cls.logged2 = Client()
        cls.logged2.force_login(PostsFormTests.user2)
        cls.form = PostForm()
        cls.guest = Client()
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
            content=PostsFormTests.small_gif,
            content_type='image/gif'
        )
        cls.gif_url = 'posts/small.gif'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст нового поста для теста формы',
            'group': PostsFormTests.group.id,
            'image': PostsFormTests.uploaded
        }
        response = PostsFormTests.logged1.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.filter(
            text=form_data['text'],
            group=PostsFormTests.group,
            author=PostsFormTests.user1
        ).order_by('-id').first()
        self.assertIsNotNone(new_post)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group, PostsFormTests.group)
        self.assertEqual(new_post.author, PostsFormTests.user1)
        self.assertEqual(new_post.image, PostsFormTests.gif_url)

    def test_edit_post(self):
        """Проверяем, что при редактировании пост изменился."""
        post_id = PostsFormTests.post.id
        form_data = {'text': 'Измененный текст поста'}
        PostsFormTests.logged1.post(
            reverse(
                'post_edit',
                args=[PostsFormTests.user1.username, post_id]
            ),
            data=form_data,
            follow=True
        )
        expected = Post.objects.filter(id=post_id).first().text
        self.assertEqual(expected, form_data['text'])

    def test_guest_cannot_create_post(self):
        """Гость не может создать пост."""
        post_count = Post.objects.count()
        redir = reverse('login') + '?next=' + reverse('new_post')
        form_data = {
            'text': 'Текст поста для гостя',
            'group': PostsFormTests.group.id
        }
        response = PostsFormTests.guest.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, redir)
        self.assertEqual(Post.objects.count(), post_count)

    def test_guest_cannot_edit_post(self):
        """Гость не может редактировать пост."""
        redir = (
            reverse('login')
            + '?next='
            + reverse(
                'post_edit',
                args=[
                    PostsFormTests.user1.username,
                    PostsFormTests.post.id
                ]
            )
        )
        post_id = PostsFormTests.post.id
        form_data = {'text': 'Измененный гостем текст поста'}
        response = PostsFormTests.guest.post(
            reverse(
                'post_edit',
                args=[PostsFormTests.user1.username, post_id]
            ),
            data=form_data,
            follow=True
        )
        check_text = Post.objects.filter(id=post_id).first().text
        self.assertRedirects(response, redir)
        self.assertNotEqual(check_text, form_data['text'])

    def test_create_comment(self):
        """Авторизованный пользователь
        может создать комментарий."""
        comm_count = Comment.objects.count()
        post_id = PostsFormTests.post.id
        form_data = {'text': 'Текст комментария'}
        response = PostsFormTests.logged2.post(
            reverse(
                'add_comment',
                args=[PostsFormTests.user1.username, post_id]
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('post', args=[PostsFormTests.user1.username, post_id])
        )
        self.assertEqual(Comment.objects.count(), comm_count + 1)
        new_comm = Comment.objects.filter(
            text=form_data['text'],
            author=PostsFormTests.user2,
            post=PostsFormTests.post
        ).order_by('-id').first()
        self.assertIsNotNone(new_comm)
        self.assertEqual(new_comm.text, form_data['text'])
        self.assertEqual(new_comm.author, PostsFormTests.user2)
        self.assertEqual(new_comm.post, PostsFormTests.post)

    def test_guest_cannot_post_comment(self):
        """Гость не может создавать комментарии."""
        comm_count = Comment.objects.count()
        redir = (
            reverse('login')
            + '?next='
            + reverse(
                'add_comment',
                args=[PostsFormTests.user1.username, PostsFormTests.post.id]
            )
        )
        post_id = PostsFormTests.post.id
        form_data = {'text': 'комментарий от гостя'}
        response = PostsFormTests.guest.post(
            reverse(
                'add_comment',
                args=[PostsFormTests.user1.username, post_id]
            ),
            data=form_data,
            follow=True
        )
        check_existance = Comment.objects.filter(
            text=form_data['text'],
            post=PostsFormTests.post
        ).exists()
        self.assertEqual(Comment.objects.count(), comm_count)
        self.assertFalse(check_existance)
        self.assertRedirects(response, redir)
