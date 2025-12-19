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
    
    def liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes_post.filter(user=user).exists()

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes_post")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")  

    def __str__(self):
        return f"{self.user} liked {self.post}"