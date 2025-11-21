from django.urls import path
from .views import GroupDetailView

app_name = "groups"

urlpatterns = [
   path("groups/<uuid:uuid>/", GroupDetailView.as_view(), name="group-detail")
]