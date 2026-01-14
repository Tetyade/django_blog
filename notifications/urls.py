from django.urls import path
from .views import NotificationListView, delete_notification, delete_all_notifications

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('delete/<uuid:uuid>/', delete_notification, name='delete'),
    path('clear-all/', delete_all_notifications, name='delete-all'),
]