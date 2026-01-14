from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class GroupConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.uuid = self.scope["url_route"]["kwargs"]["uuid"]
        self.room_group_name = f"group_{self.uuid}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_add(
            f"user_{self.user.id}",
            self.channel_name
        )

        await self.mark_messages_as_read()
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )

    async def receive(self, text_data):
        if not self.user.is_authenticated:
            return

        data = json.loads(text_data)
        text = data.get("text", "")
        user = self.user

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

        recipients = await self.get_group_user_ids(group, user)

        for user_id in recipients:
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "notify_message",
                    "text": msg.text,
                    "sender": user.username,
                    "group_name": group.name,
                    "group_uuid": str(group.uuid),
                    "created_at": msg.created_at.strftime("%H:%M"),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def notify_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_group(self):
        from .models import Group
        return Group.objects.get(uuid=self.uuid)

    @database_sync_to_async
    def get_group_user_ids(self, group, sender):
        return list(
            group.members
            .exclude(id=sender.id)
            .values_list("id", flat=True)
        )

    @database_sync_to_async
    def create_message(self, group, user, text):
        from .models import Message
        return Message.objects.create(
            group=group,
            sender=user,
            text=text
        )
    
    @database_sync_to_async
    def mark_messages_as_read(self):
        from .models import Message
        
        messages = Message.objects.filter(
            group__uuid=self.uuid
        ).exclude(
            sender=self.user
        ).exclude(
            read_by=self.user
        )

        for msg in messages:
            msg.read_by.add(self.user)
