from django.urls import path
from .views import ThreadListView, ThreadDetailView

app_name = 'messages'

urlpatterns = [
    path('', ThreadListView.as_view(), name='thread-list'),
    path('<uuid:uuid>/', ThreadDetailView.as_view(), name='thread-detail'),
]
