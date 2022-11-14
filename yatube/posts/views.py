from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import page_num


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    return render(
        request,
        'posts/index.html',
        {'page_obj': page_num(request, post_list)}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    return render(
        request,
        'posts/group_list.html',
        {'group': group, 'page_obj': page_num(request, post_list)}
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=author)
    posts = Post.objects.select_related(
        'author',
        'group'
    ).filter(author__username=username)
    return render(
        request,
        'posts/profile.html',
        {'page_obj': page_num(request, posts),
         'author': author,
         'following': following}
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    return render(
        request,
        'posts/post_detail.html',
        {'post': post, 'form': CommentForm(),
            'comments': comments}
    )


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post.id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related(
        'author'
    ).filter(author__following__user=request.user)
    return render(
        request,
        'posts/follow.html',
        {'page_obj': page_num(request, post_list)}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=author, user=request.user)
    following.delete()
    return redirect('posts:profile', author.username)
