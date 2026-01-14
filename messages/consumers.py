from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


class ThreadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.uuid = self.scope["url_route"]["kwargs"]["uuid"]
        self.room_group_name = f"thread_{self.uuid}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # група самого чату
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # персональна група користувача (для popup)
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
        await self.channel_layer.group_discard(
            f"user_{self.user.id}",
            self.channel_name
        )

    async def receive(self, text_data):
        if not self.user.is_authenticated:
            return
        data = json.loads(text_data)
        text = data["text"]

        thread = await self.get_thread()
        msg = await self.create_message(thread, self.user, text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "text": msg.text,
                "sender": self.user.username,
                "sender_uuid": str(self.user.uuid),
                "created_at": msg.created_at.strftime("%H:%M %d.%m.%Y"),
            }
        )

        # popup іншому користувачу
        other_user_id = await self.get_other_user_id(thread)
        await self.channel_layer.group_send(
            f"user_{other_user_id}",
            {
                "type": "notify_message",
                "text": msg.text,
                "sender": self.user.username,
                "created_at": msg.created_at.strftime("%H:%M"),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def notify_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "popup",
            **event
        }))

    @database_sync_to_async
    def get_thread(self):
        from .models import Thread
        return Thread.objects.get(uuid=self.uuid)

    @database_sync_to_async
    def create_message(self, thread, user, text):
        from .models import Message
        return Message.objects.create(thread=thread, sender=user, text=text)

    @database_sync_to_async
    def mark_messages_as_read(self):
        from .models import Message

        messages = Message.objects.filter(
            thread__uuid=self.uuid
        ).exclude(
            sender=self.user
        ).exclude(
            read_by=self.user
        )

        for msg in messages:
            msg.read_by.add(self.user)

    @database_sync_to_async
    def get_other_user_id(self, thread):
        return (
            thread.participant2.id
            if thread.participant1 == self.user
            else thread.participant1.id
        )
