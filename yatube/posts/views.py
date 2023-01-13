from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from posts.models import Follow, Group, Post, User
from posts.forms import CommentForm, PostForm


@cache_page(settings.CACHE_DURABILITY, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user_obj = get_object_or_404(User, username=username)
    post_list = user_obj.posts.select_related('author', 'group').all()
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user_obj': user_obj,
        'page_obj': page_obj,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=user_obj
        ).exists()
        context['following'] = following
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.select_related('author', 'post').all()
    posts_count = post.author.posts.all().count()
    context = {
        'posts_count': posts_count,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method != 'POST':
        form = PostForm()
        return render(request, template, {'form': form})
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not form.is_valid():
        return render(request, template, {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(post)
    if request.method != 'POST':
        form = PostForm(instance=post)
        context = {
            'form': form,
            'is_edit': True
        }
        return render(request, template, context)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        context = {
            'form': form,
            'is_edit': True
        }
        return render(request, template, context)
    form.save()
    return redirect(post)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(post)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = Post.objects.filter(
        author__following__user=request.user
        ).select_related('author', 'group')
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        follow = Follow.objects.get(user=request.user, author=author)
        follow.delete()
    return redirect('posts:profile', username)
