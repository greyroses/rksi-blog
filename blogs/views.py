from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BlogPostForm
from .models import BlogPost


def home(request):
    return render(request, 'blogs/home.html', {'posts': BlogPost.objects.select_related('owner')})


@login_required
def post_new(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user
            post.save()
            return redirect('blogs:home')
    else:
        form = BlogPostForm()
    return render(request, 'blogs/post_form.html', {'form': form, 'heading': 'Новая публикация'})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id, owner=request.user)
    if request.method == 'POST':
        form = BlogPostForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blogs:home')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blogs/post_form.html', {'form': form, 'heading': 'Изменить публикацию', 'post': post})
