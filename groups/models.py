import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

class Group(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_groups"
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="admin_groups",
        blank=True
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='custom_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.owner not in self.members.all():
            self.members.add(self.owner)
    
    def add_member(self, user):
        self.members.add(user)

    def remove_member(self, user):
        self.members.remove(user)

class Message(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_messages'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="read_group_messages",
        blank=True
    )

@receiver(post_save, sender=Message)
def update_group_on_new_message(sender, instance, created, **kwargs):
    if created:
        group = instance.group
        group.updated_at = instance.created_at
        group.save()
