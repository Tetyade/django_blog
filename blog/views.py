from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from blog.models import Post, Authors, Comment
from django.http import HttpResponse


def post_list(request):
    post_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(post_list, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/post_list.html', {'page_obj': page_obj})

def get_post_by_id(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse("Post not found", status=404)

    if request.method == 'POST':
        author_name = request.POST.get('author')
        comment_text = request.POST.get('text')
        if author_name and comment_text:
            Comment.objects.create(post=post, author=author_name, text=comment_text)
            return redirect('get_post_by_id', post_id=post.id)

    comments = post.comments.all().order_by('-created_at')
    context = {
        "post": post,
        "comments": comments,
    }
    return render(request, 'blog/post_detail.html', context)
    # context = {
    #     "post": post,
    # }
    # return render(request, 'blog/post_detail.html', context=context)

def get_author_by_id(request, author_id):
    try:
        author = Authors.objects.get(id=author_id)
    except Authors.DoesNotExist:
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
