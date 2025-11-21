from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Post
from comments.models import CommentLike, Comment
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'

    # def get_queryset(self):
    #     # фільтрація по тих за ким слідкуєш
    #     queryset = super().get_queryset()
    #     return queryset

class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'posts/post_detail.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.all().order_by('-created_at')  # новіші коментарі зверху

        # Тут додаємо властивість current_user для шаблону
        for comment in comments:
            comment.current_user = self.request.user

        context['comments'] = comments
        return context

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
