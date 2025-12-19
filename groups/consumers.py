from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class GroupConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.uuid = self.scope["url_route"]["kwargs"]["uuid"]
        self.room_group_name = f"group_{self.uuid}"

        # приєднання до групи
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # видалення з групи при відключенні
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data.get("text", "")
        user = self.scope["user"]

        group = await self.get_group()
        msg = await self.create_message(group, user, text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "text": msg.text,
                "sender": user.username,
                "sender_uuid": str(user.uuid),
                "created_at": msg.created_at.strftime("%H:%M %d.%m.%Y"),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_group(self):
        from .models import Group
        return Group.objects.get(uuid=self.scope["url_route"]["kwargs"]["uuid"])

    @database_sync_to_async
    def create_message(self, group, user, text):
        from .models import Message
        return Message.objects.create(group=group, sender=user, text=text)

    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.get(id=user_id)
