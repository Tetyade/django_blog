from django.urls import path
from .views import PostListView, toggle_like_post, PostCreateView, PostUpdateView, PostDeleteView
from comments.views import PostDetailWithCommentsView

app_name = 'post'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('<uuid:uuid>/', PostDetailWithCommentsView.as_view(), name='post-detail'),
    path("<uuid:uuid>/like/", toggle_like_post, name="post-like"),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('<uuid:uuid>/edit/', PostUpdateView.as_view(), name='post-edit'),
    path('<uuid:uuid>/delete/', PostDeleteView.as_view(), name='post-delete'),
]