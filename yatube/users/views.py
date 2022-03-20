from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Класс для передачи формы регистрации на
    страницу регистрации нового пользователя."""

    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = "signup.html"
