from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, F, Value, CharField, Count
from .models import Thread, Message
from .forms import MessageForm
from groups.models import Group
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()


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
            chat_type=Value('thread', output_field=CharField()), 
            unread_count=Count(
                'messages',
                filter=~Q(messages__read_by=user) & ~Q(messages__sender=user)
            )
        )

        # додаємо атрибут other_user прямо тут
        for thread in threads:
            thread.other_user = thread.participant2 if thread.participant1 == user else thread.participant1

        # Групові чати
        groups = Group.objects.filter(
            members=user
        ).annotate(
            last_update=F('updated_at'),
            chat_type=Value('group', output_field=CharField()), 
            unread_count=Count(
                'messages',
                filter=~Q(messages__read_by=user) & ~Q(messages__sender=user)
            )
        )

        # об’єднуємо та сортуємо
        combined = list(threads) + list(groups)
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
        
        if thread.participant1 == self.request.user:
            context['other_user'] = thread.participant2
        else:
            context['other_user'] = thread.participant1
        return context
    
    # def post(self, request, *args, **kwargs):
    #     thread = self.get_object()
    #     form = MessageForm(request.POST)
    #     if form.is_valid():
    #         message = form.save(commit=False)
    #         message.thread = thread
    #         message.sender = request.user
    #         message.save()
    #         thread.save()
    #         return redirect('messages:thread-detail', uuid=thread.uuid)
    #     context = self.get_context_data()
    #     context['form'] = form
    #     return self.render_to_response(context)

def start_thread(request, user_uuid):
    if not request.user.is_authenticated:
        return redirect('auth_system:login')

    other_user = get_object_or_404(User, uuid=user_uuid)

    # Перевірка, чи підписаний користувач
    if not request.user.following_set.filter(following=other_user).exists() and request.user != other_user:
        # Можна додати повідомлення, що не можна писати тим, на кого не підписаний
        from django.contrib import messages
        messages.error(request, "Ви не підписані на цього користувача.")
        return redirect('auth_system:profile-view', uuid=user_uuid)

    # Пошук існуючого thread
    thread = Thread.objects.filter(
        participant1=request.user, participant2=other_user
    ).first() or Thread.objects.filter(
        participant1=other_user, participant2=request.user
    ).first()

    # Якщо нема — створюємо новий
    if not thread:
        thread = Thread.objects.create(participant1=request.user, participant2=other_user)

    return redirect('messages:thread-detail', uuid=thread.uuid)
