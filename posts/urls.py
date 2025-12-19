from django.urls import path
from .views import PostListView, toggle_like_post
from comments.views import PostDetailWithCommentsView

app_name = 'post'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('<uuid:uuid>/', PostDetailWithCommentsView.as_view(), name='post-detail'),
    path("<uuid:uuid>/like/", toggle_like_post, name="post-like"),
]