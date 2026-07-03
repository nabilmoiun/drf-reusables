import json
from django.core.serializers.json import DjangoJSONEncoder

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.contrib.auth import get_user_model

from apps.chat.services.chat import ChatService
from apps.chat.services.websocket import SocketService
from apps.chat.services.conversation import ConversationService

User = get_user_model()

ROOM_NAME_PREFIX = "chat_"


class AuthenticatedGlobalSocketConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user_id"]
        self.room_name = f"{ROOM_NAME_PREFIX}{self.user_id}"
        self.handlers = {"chat.message": self.handle_text_message}
        if not self.user_id:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.accept()

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content, cls=DjangoJSONEncoder)

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")
        if event_type not in self.handlers.keys():
            response = await SocketService.build_socket_response(
                success=False, error="Invalid Type"
            )
            return await self.send_json(response)
        return await self.handlers[event_type](content=content)

    async def chat_message(self, event_data: dict):
        return await self.send_json(event_data["data"])

    async def handle_text_message(self, content, **kwargs):
        response = {}
        content["sender_id"] = self.user_id
        conversation_id = content.get("conversation_id")

        # The client will not send conversation id for the first message
        if not conversation_id:
            response = await ChatService.handle_initial_text_message(
                content=content, **kwargs
            )
        else:
            # After the first message, the client will always have the conversation id and send it
            response = await ChatService.handle_existing_conversation_text_message(
                content=content
            )
        if not response.get("success"):
            return await self.send_json(response)

        else:
            for user_id in (self.user_id, content.get("receiver_id")):
                await self.channel_layer.group_send(
                    f"{ROOM_NAME_PREFIX}{user_id}",
                    {"type": "chat.message", "data": response},
                )
