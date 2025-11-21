from django.shortcuts import render, get_object_or_404, redirect
from .models import Group
from django.http import HttpResponseForbidden
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MessageForm
   
class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['messages'] = group.messages.order_by('created_at')
        context['form'] = MessageForm()
        return context
    
    def post(self, request, *args, **kwargs):
        group = self.get_object()
        if request.user not in group.members.all():
            return HttpResponseForbidden("You are not a member of this group.")

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.sender = request.user
            message.save()
            group.save()
            return redirect('groups:group-detail', uuid=group.uuid)
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)
