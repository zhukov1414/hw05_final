from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User


def get_page_context(post_list, request):
    paginator = Paginator(post_list, settings.NUMBER_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.all().select_related('author', 'group')
    return render(request, 'posts/index.html', {
        'page_obj': get_page_context(post_list, request), "index": True
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_page_context(post_list, request),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    following = request.user.is_authenticated and (
        request.user.follower.filter(author=author).exists()
    )
    return render(request, 'posts/profile.html', {
        'page_obj': get_page_context(post_list, request),
        'author': author,
        "post_count": post_list.count(),
        "following": following,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    author = post.author
    post_count = author.posts.count()
    form = CommentForm(request.POST or None)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        "post_count": post_count,
        'comments': comments,
        'form': form,
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk,)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post.pk,)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': get_page_context(post_list, request),
        "follow": True
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    if follower != following:
        Follow.objects.get_or_create(user=follower, author=following)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    follower.follower.filter(author=following).delete()
    return redirect("posts:profile", username=username)
