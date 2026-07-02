from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model


User = get_user_model()


from apps.chat.models import Messaage, Conversation
from apps.chat.serializers import MessageViewSerializer


class MessageService:
    @classmethod
    @database_sync_to_async
    def create_text_message(cls, conversation: Conversation, sender: User, text: str) -> Messaage:
        return Messaage.objects.create(conversation=conversation, sender=sender, text=text)
    
    @classmethod
    @database_sync_to_async
    def build_message_response(cls, message: Messaage):
        serializer = MessageViewSerializer(message)
        return serializer.data
