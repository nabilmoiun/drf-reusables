import json

from django.core.serializers.json import DjangoJSONEncoder
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.chat.services.chat import ChatService
from apps.chat.services.websocket import SocketService


ROOM_PREFIX = "chat_"


class AuthenticatedGlobalSocketConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user:
            await self.close()
            return

        self.room_group_name = f"{ROOM_PREFIX}{self.user.id}"

        self.handlers = {
            "chat.message": self.handle_text_message,
        }

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content, cls=DjangoJSONEncoder)

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")

        handler = self.handlers.get(event_type)

        if not handler:
            response = await SocketService.build_socket_response(
                success=False,
                error="Invalid event type",
                event_type="chat.error",
            )
            return await self.send_json(response)

        return await handler(content)

    async def chat_message(self, event):
        """
        Broadcast handler (from channel layer).
        """

        await self.send_json(event["data"])

    async def handle_text_message(self, content, **kwargs):
        """
        Entry point for chat messages.
        """
        conversation_id = content.get("conversation_id")

        if not conversation_id:
            response = await ChatService.handle_initial_text_message(
                content=content,
                sender=self.user,
            )
        else:
            response = await ChatService.handle_existing_conversation_text_message(
                content=content,
                sender=self.user,
            )

        if not response.get("success"):
            return await self.send_json(response)
        
        receiver_id = content.get("receiver_id")

        # broadcast to both participants
        for user_id in {str(self.user.id), str(receiver_id)}:
            await self.channel_layer.group_send(
                f"{ROOM_PREFIX}{user_id}",
                {
                    "type": "chat.message",
                    "data": response,
                },
            )
