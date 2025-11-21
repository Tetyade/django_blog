from django.urls import path
from .views import ChatListView, ThreadDetailView

app_name = 'messages'

urlpatterns = [
    path('', ChatListView.as_view(), name='thread-list'),
    path('<uuid:uuid>/', ThreadDetailView.as_view(), name='thread-detail'),
]
