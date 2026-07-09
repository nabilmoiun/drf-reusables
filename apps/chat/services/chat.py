from channels.db import database_sync_to_async

from apps.chat.serializers import (
    TypingIndicatorSerializer,
    TextMessagePayloadSerializer,
)
from apps.chat.services.conversation import (
    ConversationService,
    ConversationError,
)
from apps.chat.services.user import UserService
from apps.chat.services.message import MessageService
from apps.chat.services.websocket import SocketService


class ChatService:

    @classmethod
    async def handle_initial_text_message(cls, content: dict, sender):
        """
        First message in a conversation (no conversation_id yet).
        """

        serializer = TextMessagePayloadSerializer(data=content)

        if not serializer.is_valid():
            return await SocketService.build_socket_response(
                success=False,
                error=serializer.errors,
                event_type="chat.error",
            )

        try:
            receiver_id = content["receiver_id"]
            text = content.get("text")

            receiver = await UserService.get_active_user_by_id(user_id=receiver_id)

            if not receiver:
                return await SocketService.build_socket_response(
                    success=False,
                    error="Receiver not found",
                    event_type="chat.error",
                )

            conversation = await database_sync_to_async(
                ConversationService.get_or_create_conversation
            )(
                sender=sender,
                receiver=receiver,
            )
            message = await MessageService.create_text_message(
                conversation=conversation,
                sender=sender,
                text=text,
            )

            data = await MessageService.build_message_response(message)

            return await SocketService.build_socket_response(
                success=True,
                error=None,
                data=data,
            )

        except ConversationError as e:
            return await SocketService.build_socket_response(
                success=False,
                error=str(e),
                event_type="chat.error",
            )

    @classmethod
    async def handle_existing_conversation_text_message(
        cls,
        content: dict,
        sender,
    ):
        """
        Messages inside an existing conversation.
        """

        serializer = TextMessagePayloadSerializer(data=content)

        if not serializer.is_valid():
            return await SocketService.build_socket_response(
                success=False,
                error=serializer.errors,
                event_type="chat.error",
            )

        try:
            receiver_id = content["receiver_id"]
            conversation_id = content["conversation_id"]
            text = content.get("text")

            receiver = await UserService.get_active_user_by_id(user_id=receiver_id)

            if not receiver:
                return await SocketService.build_socket_response(
                    success=False,
                    error="Receiver not found",
                    event_type="chat.error",
                )

            conversation = await database_sync_to_async(
                ConversationService.get_conversation
            )(
                conversation_id=conversation_id,
                sender=sender,
                receiver=receiver,
            )

            message = await MessageService.create_text_message(
                conversation=conversation,
                sender=sender,
                text=text,
            )

            data = await MessageService.build_message_response(message)

            return await SocketService.build_socket_response(
                success=True,
                error=None,
                data=data,
            )

        except ConversationError as e:
            return await SocketService.build_socket_response(
                success=False,
                error=str(e),
                event_type="chat.error",
            )

    @classmethod
    async def handle_typing_event(self, content: dict):
        serializer = TypingIndicatorSerializer(data=content)

        if not serializer.is_valid():
            response = await SocketService.build_socket_response(
                success=False, error=serializer.errors, event_type="typing.error"
            )
            return response
        sender = content["sender"]
        response = await SocketService.build_socket_response(
            success=True,
            error=None,
            data={"message": "%s is typing" % str(sender)},
            event_type="chat.typing",
        )

        return response
