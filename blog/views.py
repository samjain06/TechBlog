from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.utils import timezone
from django.urls import reverse_lazy

from blog.forms import PostForm, CommentForm
from blog.models import Post, Comment


# Create your views here.

class AboutView(TemplateView):
    template_name = 'about.html'


# Homepage
class PostListView(ListView):
    model = Post

    # Query like get_queryset lets us use ORM in Django
    def get_queryset(self):
        # '__lte' means less than or equal to. It is equivalent to WHERE clause in SQL query.
        # '-' in order_by arg means descending order. For ascending order we remove '-'
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post

    def get_queryset(self):
        # '__lte' means less than or equal to. It is equivalent to WHERE clause in SQL query.
        # '-' in order_by arg means descending order. For ascending order we remove '-'
        return Post.objects.filter(published_date__isnull=True).order_by('-create_date')


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


# COMMENTS CLASSES
@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)

    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # post_pk is initialized because it will not remember content.pk  after content removed
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)
