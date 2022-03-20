from django.contrib.auth import get_user_model
from django.db import models


class Group(models.Model):
    """Класс Group нужен для создания БД SQL со списком групп, в которые
    будут пользовтели будут делать посты."""

    title = models.CharField(verbose_name='Имя сообщества', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание сообщества')

    def __str__(self):
        return self.title


User = get_user_model()


class Post(models.Model):
    """Класс Post создает БД SQL для хранения постов пользователей."""

    text = models.TextField(verbose_name='Текст записи')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Сообщество'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    class Meta:
        ordering = ('-pub_date', '-pk')

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Класс Comment создает БД SQL для хранения комментариев пользователей."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария'
    )

    class Meta:
        ordering = ('-created', '-pk')

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """Класс Follow создает БД SQL для хранения
    информации о подписчиках и подписках."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = ['user', 'author']

    def __str__(self):
        user_str = str(self.user.username)
        author_str = str(self.author.username)
        link_str = user_str + ' - ' + author_str
        return link_str
