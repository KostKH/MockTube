from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):
    """Класс нужен для вывода на странице админа
    детальной информации по сделанным постам."""

    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Класс нужен для вывода на странице админа
    детальной информации по созданным группам."""

    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title', 'slug', 'description')
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Класс нужен для вывода на странице админа
    детальной информации по комментариям."""

    list_display = ('pk', 'post', 'author', 'text', 'created')
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
