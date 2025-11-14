from django.db import models
from django.conf import settings

class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        "posts.Post",   
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    mentioned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="mentioned_in_comments"
    )

    media = models.FileField(upload_to='comments_media/', null=True, blank=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"
    
    # @property
    # def liked_by_current_user(self):
    #     # спочатку встановимо `current_user` у view
    #     if hasattr(self, 'current_user'):
    #         return self.likes.filter(user=self.current_user).exists()
    #     return False
    
class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("comment", "user")  

    def __str__(self):
        return f"{self.user} liked {self.comment}"
   