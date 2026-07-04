from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from channels.db import database_sync_to_async

from apps.chat.models import Conversation

User = get_user_model()


class ConversationError(Exception):
    """Base conversation exception."""


class SelfConversationError(ConversationError):
    """Raised when a user tries to chat with themselves."""


class ConversationBlockedError(ConversationError):
    """Raised when the conversation is blocked."""


class ConversationNotFoundError(ConversationError):
    """Raised when the conversation does not exist."""


class ConversationService:
    """
    Service responsible for conversation-related business logic.
    """

    @staticmethod
    def normalize_users(user1: User, user2: User) -> tuple[User, User]:
        """
        Always store the lower PK first.
        This guarantees uniqueness regardless of who initiates the chat.
        """

        if user1.pk == user2.pk:
            raise SelfConversationError(
                "You cannot start a conversation with yourself."
            )

        return (user1, user2) if user1.pk < user2.pk else (user2, user1)

    @classmethod
    @database_sync_to_async
    def get_or_create_conversation(
        cls,
        sender: User,
        receiver: User,
    ) -> Conversation:

        user1, user2 = cls.normalize_users(sender, receiver)

        try:
            with transaction.atomic():

                conversation, created = Conversation.objects.get_or_create(
                    user1=user1,
                    user2=user2,
                    defaults={
                        "last_message_at": timezone.now(),
                    },
                )

                if created:
                    conversation.participants.set([user1, user2])

                return conversation

        except IntegrityError:
            # Another request created it simultaneously.
            return Conversation.objects.get(
                user1=user1,
                user2=user2,
            )

    @classmethod
    @database_sync_to_async
    def get_conversation(
        cls,
        conversation_id,
        sender: User,
        receiver: User,
    ) -> Conversation:

        user1, user2 = cls.normalize_users(sender, receiver)

        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user1=user1,
                user2=user2,
            )
        except Conversation.DoesNotExist:
            raise ConversationNotFoundError("Conversation does not exist.")

        if conversation.blocked_by:
            raise ConversationBlockedError("This conversation has been blocked.")

        return conversation

    @classmethod
    @database_sync_to_async
    def touch(
        cls,
        conversation: Conversation,
    ):
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=["last_message_at"])
