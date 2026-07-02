from typing import Tuple

from django.utils import timezone
from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async

from apps.chat.models import Conversation, Messaage
from apps.chat.serializers import MessageViewSerializer

User = get_user_model()


@database_sync_to_async
def get_or_create_conversation(
    user1: User, user2: User
) -> Tuple[Conversation | None, str | None]:
    """
    There might be situations where user can send message directly without connection request.
    As a result, we must create a conversation between two users for the first time or initial message.

    We are considering user1 always smaller than user2 and they are unique together.
    So, we can easily filter by user1 and user2 directly without annotating the participants field
    thus optimizing for large scale.
    """

    id1, id2 = user1.id, user2.id

    if id1 == id2:
        raise ValueError("Can't create a conversation with yourself")

    if id1 > id2:
        id1, id2 = id2, id1

    try:
        conversation, created = Conversation.objects.get_or_create(
            user1=user1, user2=user2, defaults={"last_message_at": timezone.now()}
        )
        if created:
            conversation.participants.add(*[user1, user2])

    except Exception as e:
        return None, str(e)

    return conversation, None


async def build_socket_response(success: bool, error: str, data: dict | None = None):
    return {"success": success, "error": error, "data": data or {}}


@database_sync_to_async
def create_text_message(conversation: Conversation, sender: User, text: str) -> Messaage:
    return Messaage.objects.create(conversation=conversation, sender=sender, text=text)


@database_sync_to_async
def build_message_response(message: Messaage):
    serializer = MessageViewSerializer(message)
    return serializer.data

