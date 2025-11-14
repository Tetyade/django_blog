import uuid
from django.db import models
from django.conf import settings


class Post(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
