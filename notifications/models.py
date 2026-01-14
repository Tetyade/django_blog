import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = settings.AUTH_USER_MODEL

class NotificationVerb(models.TextChoices):
    LIKE = "like", "liked your post"
    COMMENT = "comment", "commented on your post"
    FOLLOW = "follow", "started following you"
    COMMENT_LIKE = "comment_like", "liked your comment"

class Notification(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_sent"
    )

    verb = models.CharField(max_length=50, choices=NotificationVerb.choices)

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey(
        "target_content_type",
        "target_object_id"
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} {self.verb} → {self.recipient}"
