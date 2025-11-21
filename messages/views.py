from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Thread, Message
from .forms import MessageForm

class ThreadListView(ListView):
    model = Thread
    context_object_name = 'threads'
    template_name = 'messages/thread_list.html'

    def get_queryset(self):
        user = self.request.user
        return Thread.objects.filter(Q(participant1=user) | Q(participant2=user)).order_by('-updated_at')

class ThreadDetailView(LoginRequiredMixin, DetailView):
    model = Thread
    template_name = 'messages/thread_detail.html'
    context_object_name = 'thread'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread = self.get_object()
        messages = Message.objects.filter(thread=thread).order_by('created_at')
        context['messages'] = messages
        context['form'] = MessageForm()
        return context
    
    def post(self, request, *args, **kwargs):
        thread = self.get_object()
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            thread.save()
            return redirect('messages:thread-detail', uuid=thread.uuid)
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


