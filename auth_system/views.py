from django.shortcuts import render, get_object_or_404, redirect
# accounts/views.py
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from django.views.generic import DetailView, UpdateView
from .models import CustomUser, Follow
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from posts.models import Post, PostLike

class UserRegisterView(FormView):
    template_name = "auth_system/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("auth_system:my-profile")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = "auth_system/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy(self.get_redirect_url() or "post:home")

class MyProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "auth_system/profile.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # Всі пости користувача
        posts = user.posts.all().order_by('-created_at')

        # Додаємо властивість для шаблону (як у списку постів)
        for post in posts:
            post.post_liked_by_current_user = PostLike.objects.filter(post=post, user=self.request.user).exists()

        # Пагінація
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        return context
    
    # def get_context_data(self, **kwargs):
    #     # зробити кількість постів, кількість фоловерів та тим за ким слідкуєщ
    #     context = super().get_context_data(**kwargs)
    #     user = self.get_object()

    #     context['user-stats']

        

class ProfileView(DetailView):
    model = CustomUser
    template_name = "posts/author_detail.html"
    context_object_name = "author"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_object()
        user = self.request.user

        posts = author.posts.all().order_by('-created_at')

        if user.is_authenticated:
            for post in posts:
                post.post_liked_by_current_user = PostLike.objects.filter(post=post, user=user).exists()
        else:
            for post in posts:
                post.post_liked_by_current_user = False

        if user.is_authenticated and user != author:
            context['is_following'] = user.following_set.filter(following=author).exists()
        else:
            context['is_following'] = False

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get("page")
        context["page_obj"] = paginator.get_page(page_number)

        return context


class MyProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = "auth_system/profile_update.html"
    fields = ["username", "email", "first_name", "last_name"]

    def get_object(self, queryset=None):
        # завжди повертаємо саме поточного користувача
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy("auth_system:my-profile")
    

@login_required
def follow_user(request, user_uuid):
    user_to_follow = get_object_or_404(CustomUser, uuid=user_uuid)

    if user_to_follow == request.user:
        messages.error(request, "Не можна підписатися на себе.")
        return redirect("auth_system:profile-view", uuid=user_uuid)

    obj, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    if created:
        messages.success(request, f"Тепер ви підписані на {user_to_follow.username}!")
    else:
        messages.warning(request, f"Ви вже підписані на {user_to_follow.username}.")
    return redirect("auth_system:profile", uuid=user_uuid)


@login_required
def unfollow_user(request, user_uuid):
    user_to_unfollow = get_object_or_404(CustomUser, uuid=user_uuid)

    follow_relation = Follow.objects.filter(follower=request.user, following=user_to_unfollow).first()
    if follow_relation:
        follow_relation.delete()
        messages.success(request, f"Ви відписалися від {user_to_unfollow.username}.")
    else:
        messages.warning(request, f"Ви не були підписані на {user_to_unfollow.username}.")
    return redirect("auth_system:profile", uuid=user_uuid)

@login_required
def followers_list(request, user_uuid):
    user = get_object_or_404(CustomUser, uuid=user_uuid)
    followers = user.followers_set.all().select_related("follower")
    
    paginator = Paginator(followers, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "auth_system/followers_list.html", {
        "user_profile": user,
        "page_obj": page_obj,
        "type": "followers"
    })


@login_required
def following_list(request, user_uuid):
    user = get_object_or_404(CustomUser, uuid=user_uuid)
    following = user.following_set.all().select_related("following")

    paginator = Paginator(following, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "auth_system/following_list.html", {
        "user_profile": user,
        "page_obj": page_obj,
        "type": "following"
    })
