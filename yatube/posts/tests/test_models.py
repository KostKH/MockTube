from django.test import TestCase

from posts.models import Group, Post, User


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='UserForTest')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testgroup',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст длинною больше 15 символов.',
            author=PostsModelsTest.user,
            group=PostsModelsTest.group,
        )

    def test_post_str_is_text(self):
        """Проверяем, что при вызове экземпляра класса Post
        в качестве описания выдаются первые 15 символов поста."""
        sample = str(PostsModelsTest.post)
        expected = PostsModelsTest.post.text[:15]
        self.assertEquals(sample, expected)

    def test_group_str_is_title(self):
        """Проверяем, что при вызове экземпляра класса Group
        в качестве описания выдается имя группы."""
        sample = str(PostsModelsTest.group)
        expected = PostsModelsTest.group.title
        self.assertEquals(sample, expected)
