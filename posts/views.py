from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, PostLike
from comments.models import CommentLike, Comment
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        qs = super().get_queryset().order_by('-created_at')
        # Додаємо властивість liked_by_current_user для кожного поста
        for post in qs:
            post.post_liked_by_current_user = post.likes_post.filter(user=self.request.user).exists()
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

