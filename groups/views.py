from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import Group
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MessageForm, GroupForm, GroupCreateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from auth_system.models import Follow

User = get_user_model()
   
class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'groups/group_detail.html'
    context_object_name = 'group'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_role(self, group, user):
        if user == group.owner:
            return "owner"
        elif user in group.admins.all():
            return "admin"
        else:
            return "member"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()

        context['messages'] = group.messages.order_by('created_at')
        context['form'] = MessageForm()
        context['role'] = self.get_role(group, self.request.user)
        context['members'] = group.members.all()
        context['admins'] = group.admins.all()
        context['users'] = group.members.all()

        return context

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupCreateForm
    template_name = 'groups/group_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        group = form.save(commit=False)
        group.owner = self.request.user
        group.save()
        group.members.add(self.request.user)
        for member in form.cleaned_data['members']:
            group.members.add(member)
        messages.success(self.request, f"Група '{group.name}' створена успішно!")
        return redirect('groups:group-detail', uuid=group.uuid)

@login_required
def search_mutual_followers(request):
    query = request.GET.get('q', '').strip()
    user = request.user
    mutual_followers = user.following_set.filter(
        following__followers_set__follower=user
    )

    if query:
        mutual_followers = mutual_followers.filter(
            following__username__icontains=query
        )
    data = [{"id": f.following.id, "username": f.following.username} for f in mutual_followers]
    return JsonResponse(data, safe=False)



@login_required
def update_group(request, uuid):
    group = get_object_or_404(Group, uuid=uuid)
    user = request.user
    mutual_followers = user.following_set.filter(following__following_set__following=user)
    print(mutual_followers)

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            group.name = name
            group.save()
            messages.success(request, "Назву оновлено.")
        return redirect("groups:group-detail", uuid=uuid)

    return render(request, "groups/update.html", {"group": group})

@login_required
def remove_member(request, uuid, user_id):
    group = get_object_or_404(Group, uuid=uuid)
    user = get_object_or_404(User, id=user_id)

    if request.user not in [group.owner] and request.user not in group.admins.all():
        messages.error(request, "У вас немає прав.")
        return redirect("groups:group-detail", uuid=uuid)

    if user == group.owner:
        messages.error(request, "Неможливо видалити власника.")
        return redirect("groups:group-detail", uuid=uuid)

    if user in group.admins.all() and request.user != group.owner:
        messages.error(request, "Тільки власник може видаляти адмінів.")
        return redirect("groups:group-detail", uuid=uuid)

    group.members.remove(user)
    group.admins.remove(user)

    messages.success(request, f"Користувача {user.username} видалено.")
    return redirect("groups:group-detail", uuid=uuid)

@login_required
def leave_group(request, uuid):
    group = get_object_or_404(Group, uuid=uuid)
    user = request.user

    if user not in group.members.all():
        return HttpResponseForbidden("Ви не в цій групі.")

    if user == group.owner:
        admins = group.admins.all()
        if admins.exists():
            new_owner = admins.first()
            group.owner = new_owner
            group.admins.remove(new_owner)
            messages.info(request, f"Новий власник групи: {new_owner.username}")
        else:
            members = group.members.exclude(id=user.id)
            if members.exists():
                new_owner = members.first()
                group.owner = new_owner
                messages.info(request, f"Новий власник групи: {new_owner.username}")
            else:
                group.delete()
                messages.success(request, "Групу видалено, бо ви були останнім учасником.")
                return redirect("messages:thread-list")

        group.save()

    group.members.remove(user)
    messages.success(request, "Ви вийшли з групи.")
    return redirect("messages:thread-list")

def delete_group(request, uuid):
    group = get_object_or_404(Group, uuid=uuid)

    if request.user != group.owner:
        return HttpResponseForbidden("Тільки власник може видалити групу.")

    group.delete()
    messages.success(request, "Групу видалено.")
    return redirect("messages:thread-list")

@login_required
def add_admin(request, uuid, user_id):
    group = get_object_or_404(Group, uuid=uuid)
    user = get_object_or_404(User, id=user_id)

    # Тільки власник може призначати адмінів
    if request.user != group.owner:
        messages.error(request, "Тільки власник може призначати адмінів.")
        return redirect("groups:group-detail", uuid=uuid)

    # Не можна зробити адміном власника (він і так головний)
    if user == group.owner:
        messages.error(request, "Власник і так має всі права.")
        return redirect("groups:group-detail", uuid=uuid)

    # Якщо користувача немає серед учасників — не можна
    if user not in group.members.all():
        messages.error(request, "Цей користувач не є учасником групи.")
        return redirect("groups:group-detail", uuid=uuid)

    group.admins.add(user)
    messages.success(request, f"{user.username} тепер адмін групи!")
    return redirect("groups:group-detail", uuid=uuid)

@login_required
def remove_admin(request, uuid, user_id):
    group = get_object_or_404(Group, uuid=uuid)
    user = get_object_or_404(User, id=user_id)

    # Тільки власник може знімати адмінів
    if request.user != group.owner:
        messages.error(request, "Тільки власник може знімати адмінів.")
        return redirect("groups:group-detail", uuid=uuid)

    # Неможливо забрати роль у власника
    if user == group.owner:
        messages.error(request, "Неможливо змінити роль власника групи.")
        return redirect("groups:group-detail", uuid=uuid)

    group.admins.remove(user)
    messages.success(request, f"{user.username} більше не адмін.")
    return redirect("groups:group-detail", uuid=uuid)

@login_required
def add_member(request, uuid):
    group = get_object_or_404(Group, uuid=uuid)

    # Тільки owner або admin може додавати
    if request.user != group.owner and request.user not in group.admins.all():
        messages.error(request, "У вас немає прав додавати користувачів.")
        return redirect("groups:group-detail", uuid=uuid)

    if request.method == "POST":
        username = request.POST.get("username").strip()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Користувача з таким username не існує.")
            return redirect("groups:group-detail", uuid=uuid)

        # Перевірка взаємних фоловерів
        is_mutual = Follow.objects.filter(follower=request.user, following=user).exists() and \
                    Follow.objects.filter(follower=user, following=request.user).exists()
        if not is_mutual:
            messages.error(request, f"{user.username} не є вашим взаємним фоловером.")
            return redirect("groups:group-detail", uuid=uuid)

        if user in group.members.all():
            messages.warning(request, f"{user.username} вже у групі.")
            return redirect("groups:group-detail", uuid=uuid)

        group.members.add(user)
        messages.success(request, f"{user.username} додано до групи!")
        return redirect("groups:group-detail", uuid=uuid)