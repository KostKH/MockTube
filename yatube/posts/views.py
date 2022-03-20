from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from django.http import JsonResponse
from .serializers import PostSerializer


def index(request):
    """Функция возвращает объект класса BaseManager (результат SQL-запроса),
    который содержит посты в БД Posts, и передает его в шаблон index.html."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    """Функция возвращает объект класса BaseManager (результат SQL-запроса),
    который содержит посты из БД Posts с фильтром по заданной группе. В шаблон
    group.html передаются записи с постами и данные по группе."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


def profile(request, username):
    """Формируем данные для страницы профайла - список постов автора,
    поделенный на страницы. передаем данные в шаблон страниц."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user in User.objects.all():
        following = (
            Follow
            .objects
            .filter(author=author, user=request.user)
            .exists()
        )
    else:
        following = False
    user_not_author = (request.user != author)
    params = {
        'author': author,
        'page': page,
        'following': following,
        'user_not_author': user_not_author
    }
    return render(request, 'profile.html', params)


def post_view(request, username, post_id):
    """Формируем данные для страницы поста - отбираем нужный
    пост из базы, передаем в шаблон страницы."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm(request.POST or None)
    if request.user in User.objects.all():
        following = (
            Follow
            .objects
            .filter(author=post.author, user=request.user)
            .exists()
        )
    else:
        following = False
    user_not_author = (request.user != post.author)
    params = {
        'author': post.author,
        'post': post,
        'form': form,
        'comments': comments,
        'following': following,
        'user_not_author': user_not_author
    }
    return render(request, 'post.html', params)


@login_required
def new_post(request):
    """Генерим форму для создания нового поста,
    передаем данные в шаблон страницы, получаем
    данные из формы и созраняем в базе данных."""
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new.html', {'form': form})
    form = PostForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    """Генерим форму для редактирования поста,
    передаем данные в шаблон страницы, получаем
    данные из формы и созраняем в базе данных."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post_edit', username=username, post_id=post_id)
    context = {
        'form': form,
        'edit': True,
        'post': post
    }
    return render(request, 'new.html', context)


def page_not_found(request, exception=None):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    """Генерим форму для создания нового комментария,
    передаем данные в шаблон страницы, получаем
    данные из формы и созраняем в базе данных."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comm = form.save(commit=False)
        comm.author = request.user
        comm.post = post
        comm.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.PAGE_NO)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author == user:
        return redirect('profile', username)
    if not Follow.objects.filter(author=author, user=user).exists():
        Follow.objects.create(author=author, user=user)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if Follow.objects.filter(author=author, user=user).exists():
        link = Follow.objects.filter(author=author, user=user).first()
        link.delete()
    return redirect('profile', username)


def get_post(request, pk):
    if request.method == 'GET':
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post)
        json_response = JsonResponse(serializer.data)
        return json_response
