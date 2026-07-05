from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.chat.models import Conversation, Attachment, Message


User = get_user_model()


class BaseSenderViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name") 


class CreateConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        exclude = ("last_message_at", "participants")


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"


class MessageViewSerializer(serializers.ModelSerializer):

    sender = BaseSenderViewSerializer(read_only=True)
    conversation_id = serializers.UUIDField(source="conversation", read_only=True)
    attachments = AttachmentSerializer(read_only=True, many=True)
    
    class Meta:
        model = Message
        exclude = ("conversation",)
        

class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ("user",)


class TextMessagePayloadSerializer(serializers.Serializer):
    receiver_id = serializers.CharField()
    conversation_id = serializers.CharField(required=False)
    text = serializers.CharField()


class TypingIndicatorSerializer(serializers.Serializer):
    conversation_id = serializers.CharField()
    receiver_id = serializers.CharField()


class BaseChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class ConversationListSerializer(serializers.ModelSerializer):
    
    chat_user = serializers.SerializerMethodField()
    last_message = MessageViewSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        exclude = ("participants", "user1", "user2")

    def get_chat_user(self, obj):
        user = self.context["request"].user
        other_user = obj.get_other_conversation_user(user)
        return BaseChatUserSerializer(other_user).data

