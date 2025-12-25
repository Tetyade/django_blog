import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings')


from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from channels.auth import AuthMiddlewareStack

from messages.consumers import ThreadConsumer
from groups.consumers import GroupConsumer
from notifications.consumers import NotificationConsumer

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/thread/<uuid:uuid>/", ThreadConsumer.as_asgi()),
            path("ws/group/<uuid:uuid>/", GroupConsumer.as_asgi()),
            path("ws/notifications/", NotificationConsumer.as_asgi()),
        ])
    )
})
