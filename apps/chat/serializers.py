from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.chat.models import Conversation, Attachment, Messaage


User = get_user_model()


class BaseSenderViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name") 


class CreateConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        exclude = ("last_message_at", "participants")


class MessageViewSerializer(serializers.ModelSerializer):

    sender = BaseSenderViewSerializer(read_only=True)
    conversation_id = serializers.UUIDField(source="conversation", read_only=True)
    
    class Meta:
        model = Messaage
        exclude = ("conversation",)
        

class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messaage
        exclude = ("user",)


class TextMessagePayloadSerializer(serializers.Serializer):
    sender_id = serializers.CharField()
    receiver_id = serializers.CharField()
    conversation_id = serializers.CharField(required=False)
    text = serializers.CharField()




    

