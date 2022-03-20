from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Класс для вывода страницы об авторе."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Класс для вывода страницы о технологиях."""

    template_name = 'about/tech.html'
