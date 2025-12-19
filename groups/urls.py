from django.urls import path
from . import views

app_name = "groups"

urlpatterns = [
    path("<uuid:uuid>/add-admin/<int:user_id>/", views.add_admin, name="add-admin"),
    path("<uuid:uuid>/remove-admin/<int:user_id>/", views.remove_admin, name="remove-admin"),

    path("<uuid:uuid>/remove-member/<int:user_id>/", views.remove_member, name="remove-member"),
    path("<uuid:uuid>/leave/", views.leave_group, name="leave-group"),
    path("<uuid:uuid>/delete/", views.delete_group, name="delete-group"),
    path("<uuid:uuid>/update/", views.update_group, name="update"),
    path("<uuid:uuid>/", views.GroupDetailView.as_view(), name="group-detail"),
    path("<uuid:uuid>/add-member/", views.add_member, name="add-member"),
    path("create/", views.GroupCreateView.as_view(), name="create-group"),
    path('ajax/search-followers/', views.search_mutual_followers, name='search-followers'),


]
