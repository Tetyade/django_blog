import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Thread(models.Model):
    participant1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='threads_as_participant1'
    )
    participant2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='threads_as_participant2'
    )
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant1', 'participant2')

    def __str__(self):
        return f"Thread between {self.participant1.username} and {self.participant2.username}"

class Message(models.Model):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='direct_messages'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def to_json(self):
        return {
            "id": self.id,
            "sender": self.sender.username,
            "text": self.text,
            "created_at": self.created_at.isoformat()
        }


@receiver(post_save, sender=Message)
def update_thread_on_new_message(sender, instance, created, **kwargs):
    if created:
        thread = instance.thread
        thread.updated_at = instance.created_at
        thread.save()