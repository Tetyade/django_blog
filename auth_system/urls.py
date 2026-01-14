from django.urls import path
from .views import UserLoginView, UserRegisterView, ProfileView, MyProfileView, MyProfileUpdateView, follow_user, unfollow_user, followers_list, following_list, search_users
# from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy

app_name = "auth_system"

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="post:home"), name="logout"),
    path("profile/", MyProfileView.as_view(), name="my-profile"),
    path("profile/edit/", MyProfileUpdateView.as_view(), name="my-profile-edit"),
    path("profile/<uuid:uuid>/", ProfileView.as_view(), name="profile"),
    # password reset
    path("password_reset/", PasswordResetView.as_view(template_name='auth_system/password_form.html', 
        email_template_name='auth_system/password_reset_email.html',
        extra_context={'submit_text': 'Send Email', 'message': 'Enter your email and we will send instructions.'}, 
        success_url=reverse_lazy('auth_system:password_reset_done'), 
    ), name='password_reset'),
    path("password_reset/done/", PasswordResetDoneView.as_view(template_name='auth_system/password_form.html',
        extra_context={'message': 'Instructions email sent. Check your inbox.'}
    ), name='password_reset_done'),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(template_name='auth_system/password_reset_confirm.html',
        extra_context={'submit_text': 'Save', 'message': 'Enter your new password below:'}, 
        success_url=reverse_lazy('auth_system:password_reset_complete'),
    ), name='password_reset_confirm'),
    path("reset/done/", PasswordResetCompleteView.as_view(template_name='auth_system/password_form.html',
        extra_context={'message': 'Password successfully changed. You can now log in.'}
    ), name='password_reset_complete'),
    #     template_name='auth_system/reset/password_reset.html'), name="password_reset"),
    # path("password_reset/done/", PasswordResetDoneView.as_view(template_name='auth_system/reset/password_reset_done.html'), name="password_reset_done"),
    # path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(template_name='auth_system/reset/password_reset_confirm.html'), name="password_reset_confirm"),
    # path("reset/done/", PasswordResetCompleteView.as_view(template_name='auth_system/reset/password_reset_complete.html'), name="password_reset_complete"),
    path("follow/<uuid:user_uuid>/", follow_user, name="follow"),
    path("unfollow/<uuid:user_uuid>/", unfollow_user, name="unfollow"),
    path("followers/<uuid:user_uuid>/", followers_list, name="followers-list"),
    path("following/<uuid:user_uuid>/", following_list, name="following-list"),
    path("search/", search_users, name="user-search"),
]

