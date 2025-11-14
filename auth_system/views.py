from django.shortcuts import render, get_object_or_404, redirect
# accounts/views.py
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from django.views.generic import DetailView, UpdateView
from .models import CustomUser
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from posts.models import Post

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

        posts = author.posts.all().order_by('-created_at')

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        return context

class MyProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = "auth_system/profile_update.html"
    fields = ["username", "email", "first_name", "last_name"]

    def get_object(self, queryset=None):
        # завжди повертаємо саме поточного користувача
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy("auth:my-profile")