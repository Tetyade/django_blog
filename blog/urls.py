from django.urls import path
import blog.views as views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:post_id>/', views.get_post_by_id, name='get_post_by_id'),
    path('authors/<int:author_id>/', views.get_author_by_id, name='get_author_by_id'),
]