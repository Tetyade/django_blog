from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from .models import Notification, NotificationVerb
from django.contrib.auth import get_user_model

User = get_user_model()

from posts.models import PostLike, Post


@receiver(post_save, sender=PostLike)
def post_liked_notification(sender, instance, created, **kwargs):
    if not created:
        return

    post = instance.post
    actor = instance.user
    recipient = post.author

    if actor == recipient:
        return  # не повідомляємо себе

    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=NotificationVerb.LIKE,
        target=post
    )


from comments.models import Comment


@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if not created:
        return

    actor = instance.author
    post = instance.post
    recipient = post.author

    if actor == recipient:
        return

    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=NotificationVerb.COMMENT,
        target=post
    )


from auth_system.models import Follow


@receiver(post_save, sender=Follow)
def follow_notification(sender, instance, created, **kwargs):
    if not created:
        return

    actor = instance.follower
    recipient = instance.following

    if actor == recipient:
        return

    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=NotificationVerb.FOLLOW,
        target=recipient
    )

