from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from .models import Post, PostLike
from comments.models import CommentLike, Comment
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .forms import PostForm

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        for post in qs:
            if self.request.user.is_authenticated:
                post.post_liked_by_current_user = post.likes_post.filter(user=self.request.user).exists()
            else:
                post.post_liked_by_current_user = False
        return qs

    # def get_queryset(self):
    #     # фільтрація по тих за ким слідкуєш
    #     queryset = super().get_queryset()
    #     return queryset

def get_author_by_id(request, author_id):
    try:
        author = settings.AUTH_USER_MODEL.objects.get(id=author_id)
    except settings.AUTH_USER_MODEL.DoesNotExist:
        return render(request, 'blog/author_not_found.html', status=404)
    
    posts = author.posts.all().order_by('-created_at')
    paginator = Paginator(posts, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "author": author,
        "page_obj": page_obj,
    }
    return render(request, 'blog/author_detail.html', context=context)

@require_POST
@login_required
def toggle_like_post(request, uuid):
    post = get_object_or_404(Post, uuid=uuid)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': post.likes_post.filter(user=request.user).exists(),
            'likes_count': post.likes_post.count()
        })

    return redirect("post:post-detail", uuid=post.uuid)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('post:home') # Куди перекине після видалення
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_queryset(self):
        # Це гарантує, що видалити може ТІЛЬКИ автор
        return Post.objects.filter(author=self.request.user)
