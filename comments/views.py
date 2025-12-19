from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, View
from .models import Comment
from .forms import CommentForm
from posts.models import Post, PostLike
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
# from notifications.utils import process_mentions
from comments.models import CommentLike
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


class PostDetailWithCommentsView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = self.object.comments.all().order_by("-created_at")
        post = self.object
        post.post_liked_by_current_user = False
        if self.request.user.is_authenticated:
            post.post_liked_by_current_user = PostLike.objects.filter(post=post, user=self.request.user).exists()
        # додаємо лайкнуто чи ні
        for c in comments:
            c.liked_by_current_user = CommentLike.objects.filter(
                comment=c,
                user=self.request.user
            ).exists()

        context["comments"] = comments
        context["form"] = CommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST, request.FILES)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = self.object
            comment.save()
            return redirect("post:post-detail", uuid=self.object.uuid)

        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)
# class PostDetailWithCommentsView(LoginRequiredMixin, DetailView):
#     model = Post
#     template_name = "posts/post_detail.html"
#     context_object_name = "post"
#     slug_field = 'uuid'
#     slug_url_kwarg = 'uuid'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         comments = self.object.comments.all().order_by("-created_at")
#         for c in comments:
#             c.liked_by_current_user = CommentLike.objects.filter(
#                 comment=c,
#                 user=self.request.user
#             ).exists()
#         # context["comments"] = self.object.comments.select_related("author")
#         context["comments"] = comments
#         context["form"] = CommentForm()
#         return context
    
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = CommentForm(request.POST, request.FILES)

#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.author = request.user
#             comment.post = self.object

#             # викликаємо утиліту
#             # comment.content = process_mentions(comment, request.user)

#             comment.save()
#             return redirect("post:post-detail", uuid=self.object.uuid)

#         context = self.get_context_data()
#         context["form"] = form
#         return self.render_to_response(context)

class CommentDeleteView(UserPassesTestMixin, View):

    def test_func(self):
        # admin or staff only
        return self.request.user.is_staff or self.request.user.is_superuser
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        post_pk = comment.post.pk
        comment.delete()
        return redirect("post:post-detail", pk=post_pk)
    
@login_required
def toggle_like(request, comment_id):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        comment = get_object_or_404(Comment, pk=comment_id)
        like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
        if not created:
            like.delete()  # toggle

        data = {
            "liked": comment.likes.count() if like.pk else False,
            "likes_count": comment.likes.count(),
            "user_liked": comment.likes.filter(user=request.user).exists()
        }
        return JsonResponse({
            "liked": like.pk is not None,  # True якщо лайк створений
            "likes_count": comment.likes.count()
        })

    # якщо не AJAX або не POST
    return JsonResponse({"error": "Invalid request"}, status=400)