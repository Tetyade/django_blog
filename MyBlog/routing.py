from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from messages.consumers import ThreadConsumer
from groups.consumers import GroupConsumer

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/thread/<uuid:uuid>/", ThreadConsumer.as_asgi()),
            path("ws/group/<uuid:uuid>/", GroupConsumer.as_asgi()),
        ])
    ),
})
