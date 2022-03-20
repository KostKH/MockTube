from django.apps import AppConfig


class PostsConfig(AppConfig):
    """Класс нужен для конфигурации класса Post. В частности, дано
    название класса для целей вывода на странице админа."""

    name = 'posts'
    verbose_name = 'Управление постами и группами'
