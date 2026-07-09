from typing import List

from django.db import transaction
from django.utils import timezone
from channels.db import database_sync_to_async

from django.contrib.auth import get_user_model

from apps.chat.models import Message, Attachment
from apps.chat.serializers import MessageViewSerializer
from apps.chat.services.conversation import ConversationService

User = get_user_model()


class MessageServiceError(Exception):
    pass


class MessageService:
    """
    Handles message creation and response building.
    """

    @classmethod
    @database_sync_to_async
    def create_text_message(
        cls,
        conversation,
        sender: User,
        text: str,
    ) -> Message:

        if not text or not text.strip():
            raise MessageServiceError("Message text cannot be empty.")

        with transaction.atomic():

            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                text=text.strip(),
                type=Message.MessageType.TEXT,
            )

            # keep conversation in sync
            conversation.last_message_at = timezone.now()
            conversation.last_message = message
            conversation.save(update_fields=["last_message_at", "last_message"])

        return message
    
    @classmethod
    def create_attachment_message(
        cls,
        conversation,
        sender: User,
        text: str,
        attachments: List[Attachment]
    ) -> Message:

        with transaction.atomic():
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                text=text.strip(),
                type=Message.MessageType.TEXT,
            )
            message.attachments.add(*Attachment.objects.bulk_create(attachments))

            # keep conversation in sync
            conversation.last_message_at = timezone.now()
            conversation.last_message = message
            conversation.save(update_fields=["last_message_at", "last_message"])

        return message

    @classmethod
    @database_sync_to_async
    def build_message_response(cls, message: Message) -> dict:
        return MessageViewSerializer(message).data
