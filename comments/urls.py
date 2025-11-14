from django.urls import path
from .views import toggle_like, CommentDeleteView

app_name = 'comments'

urlpatterns = [
    path("comment/<int:comment_id>/like/", toggle_like, name="comment-like"),
    path("comments/<int:pk>/delete/", CommentDeleteView.as_view(), name="comment-delete"),

]