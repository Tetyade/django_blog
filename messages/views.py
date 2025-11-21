from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F, Value, CharField
from .models import Thread, Message
from .forms import MessageForm
from groups.models import Group


# class ThreadListView(ListView):
#     model = Thread
#     context_object_name = 'threads'
#     template_name = 'messages/thread_list.html'

#     def get_queryset(self):
#         user = self.request.user
#         return Thread.objects.filter(Q(participant1=user) | Q(participant2=user)).order_by('-updated_at')

class ChatListView(LoginRequiredMixin, ListView):
    template_name = 'messages/chat_list.html'
    context_object_name = 'chats'

    def get_queryset(self):
        user = self.request.user

        # 1-на-1 чати
        threads = Thread.objects.filter(
            Q(participant1=user) | Q(participant2=user)
        ).annotate(
            last_update=F('updated_at'),
            chat_type=Value('thread', output_field=CharField())
        )

        # Групові чати
        groups = Group.objects.filter(
            members=user
        ).annotate(
            last_update=F('updated_at'),
            chat_type=Value('group', output_field=CharField())
        )

        # перетворюємо queryset у списки і об’єднуємо
        combined = list(threads) + list(groups)

        # Сортування по останньому оновленню
        combined.sort(key=lambda obj: obj.last_update, reverse=True)

        return combined


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


