from django.urls import path
import blog.views as views

urlpatterns = [
    path('', views.post_list, name='post_list'),
]