from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification, NotificationVerb
from django.contrib.auth import get_user_model

User = get_user_model()

def send_notification_to_websocket(notification):
    channel_layer = get_channel_layer()
    
    text_map = {
        NotificationVerb.LIKE: "вподобав(ла) ваш допис",
        NotificationVerb.COMMENT: "прокоментував(ла) ваш допис",
        NotificationVerb.FOLLOW: "підписався(-лась) на вас",
        NotificationVerb.COMMENT_LIKE: "вподобав(ла) ваш коментар",
    }
    text = text_map.get(notification.verb, "нова активність")

    avatar_url = ""
    try:
        if hasattr(notification.actor, 'profile') and notification.actor.profile.avatar:
            avatar_url = notification.actor.profile.avatar.url
    except Exception:
        avatar_url = ""

    target_url = "#"
    try:
        if notification.verb in [NotificationVerb.COMMENT, NotificationVerb.COMMENT_LIKE]:
             if hasattr(notification.target, 'post') and hasattr(notification.target.post, 'get_absolute_url'):
                target_url = notification.target.post.get_absolute_url()
             elif hasattr(notification.target, 'get_absolute_url'): 
                target_url = notification.target.get_absolute_url()
        
        elif hasattr(notification.target, 'get_absolute_url'):
            target_url = notification.target.get_absolute_url()
        elif notification.verb == NotificationVerb.FOLLOW:
             if hasattr(notification.actor, 'profile') and hasattr(notification.actor.profile, 'get_absolute_url'):
                 target_url = notification.actor.profile.get_absolute_url()
             else:
                 from django.urls import reverse
                 target_url = reverse('auth_system:profile-view', kwargs={'uuid': notification.actor.uuid})

    except Exception as e:
        print(f"Error generating target_url: {e}")
        target_url = "#"

    from django.urls import reverse
    try:
        actor_url = reverse('auth_system:profile-view', kwargs={'uuid': notification.actor.uuid})
    except:
        actor_url = "#"

    async_to_sync(channel_layer.group_send)(
        f"user_{notification.recipient.id}",
        {
            "type": "notify_message",
            "sender": notification.actor.username,
            "text": text,
            "created_at": "Тільки що", 
            "notification_uuid": str(notification.uuid),
            "actor_url": actor_url, 
            "avatar_url": avatar_url,
            "target_url": target_url,
            "is_on_list_page": True
        }
    )
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

    notif = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=NotificationVerb.LIKE,
        target=post
    )
    send_notification_to_websocket(notif)

from comments.models import Comment, CommentLike


@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    if not created:
        return

    actor = instance.author
    post = instance.post
    recipient = post.author

    if actor == recipient: return

    notif = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=NotificationVerb.COMMENT,
        target=instance
    )
    send_notification_to_websocket(notif)


from auth_system.models import Follow


@receiver(post_save, sender=Follow)
def follow_notification(sender, instance, created, **kwargs):
    if not created:
        return

    actor = instance.follower
    recipient = instance.following

    if actor == recipient:
        return

    notif = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=NotificationVerb.FOLLOW,
        target=recipient
    )
    send_notification_to_websocket(notif)

@receiver(post_save, sender=CommentLike)
def comment_like_notification(sender, instance, created, **kwargs):
    if not created: return

    actor = instance.user
    comment = instance.comment
    recipient = comment.author

    if actor == recipient: return

    notif = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=NotificationVerb.COMMENT_LIKE,
        target=comment
    )
    send_notification_to_websocket(notif)
