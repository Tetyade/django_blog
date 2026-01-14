from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        unread_notifications = self.get_queryset().filter(is_read=False)
        if unread_notifications.exists():
            unread_notifications.update(is_read=True)
            
        return context

@login_required
def delete_notification(request, uuid):
    notification = get_object_or_404(Notification, uuid=uuid, recipient=request.user)
    
    notification.delete()
    messages.success(request, "Notification cleared.")
    
    return redirect('notifications:list')

@login_required
def delete_all_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, "All notifications cleared.")
    return redirect('notifications:list')
