from django.urls import path
from .views import ChatListView, ThreadDetailView, start_thread

app_name = 'messages'

urlpatterns = [
    path('', ChatListView.as_view(), name='thread-list'),
    path('<uuid:uuid>/', ThreadDetailView.as_view(), name='thread-detail'),
    path('start-thread/<uuid:user_uuid>/', start_thread, name='start-thread'),
]
