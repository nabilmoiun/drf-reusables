from apps.chat.serializers import TextMessagePayloadSerializer

from apps.chat.services.user import UserService
from apps.chat.services.message import MessageService
from apps.chat.services.websocket import SocketService
from apps.chat.services.conversation import ConversationService


class ChatService:
    @classmethod
    async def handle_initial_text_message(cls, content: dict, **kwargs):
        serializer = TextMessagePayloadSerializer(data=content)
        if not serializer.is_valid():
            response = await SocketService.build_socket_response(
                success=False, error=str(serializer.errors), event_type="chat.error"
            )
            return response

        sender = await UserService.get_user_by_id(user_id=content["sender_id"])
        receiver = await UserService.get_active_user_by_id(
            user_id=content["receiver_id"]
        )

        if not receiver:
            response = await SocketService.build_socket_response(
                success=False,
                error="No reciever found with the provided receiver_id",
                event_type="chat.error",
            )
            return response

        conversation, error = await ConversationService.get_or_create_conversation(
            user1=sender, user2=receiver
        )
        if not error:
            message = await MessageService.create_text_message(
                conversation=conversation, sender=sender, text=content.get("text")
            )
            data = await MessageService.build_message_response(message=message)
            response = await SocketService.build_socket_response(
                success=True,
                error=None,
                data=data,
            )
            return response
        else:
            response = await SocketService.build_socket_response(
                success=False, error=error, data={}, event_type="chat.error"
            )
            return response

    @classmethod
    async def handle_existing_conversation_text_message(cls, content: dict, **kwargs):
        sender_id = content["sender_id"]
        receiver_id = content["receiver_id"]
        conversation_id = content["conversation_id"]
        
        sender = await UserService.get_user_by_id(user_id=sender_id)
        receiver = await UserService.get_active_user_by_id(user_id=receiver_id)

        if not receiver:
            response = await SocketService.build_socket_response(
                success=False,
                error="No reciever found with the provided receiver_id",
                event_type="chat.error",
            )
            return response

        conversation = await ConversationService.get_chat_conversation(
            conversation_id=conversation_id, user1=sender, user2=receiver
        )

        if not conversation:
            response = await SocketService.build_socket_response(
                success=False,
                error="Invalid chat conversation",
                event_type="chat.error",
            )
            return response

        message = await MessageService.create_text_message(
            conversation=conversation, sender=sender, text=content.get("text")
        )
        data = await MessageService.build_message_response(message=message)
        response = await SocketService.build_socket_response(
            success=True,
            error=None,
            data=data,
        )
        return response
