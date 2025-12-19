from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class ThreadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.uuid = self.scope["url_route"]["kwargs"]["uuid"]
        self.room_group_name = f"thread_{self.uuid}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = data["text"]
        user = self.scope["user"]

        thread = await self.get_thread()
        msg = await self.create_message(thread, user, text)

        # Відправка всім учасникам групи з uuid відправника
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "text": msg.text,
                "sender": user.username,
                "sender_uuid": str(user.uuid),   # додано
                "created_at": msg.created_at.strftime("%H:%M %d.%m.%Y"),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_thread(self):
        from .models import Thread
        return Thread.objects.get(uuid=self.uuid)

    @database_sync_to_async
    def create_message(self, thread, user, text):
        from .models import Message
        return Message.objects.create(thread=thread, sender=user, text=text)
