from django.shortcuts import render
from blog.models import Post, Authors

def post_list(request):
    posts = Post.objects.all()
    context = {
        "posts": posts,
    }
    return render(request, 'blog/post_list.html', context=context)
