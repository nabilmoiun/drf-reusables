from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from drf_spectacular.utils import extend_schema

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status, parsers

from apps.chat.models import Conversation, Message, Attachment
from apps.chat.serializers import (
    ConversationListSerializer,
    MessageViewSerializer,
    CreateMessageSerializer,
    CreateAttachmentMessageSerializer,
)

from apps.chat.services.conversation import ConversationService

User = get_user_model()


@extend_schema(tags=["chat"])
class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationListSerializer
    queryset = Conversation.objects.order_by("last_message_at")
    serializer_class_map = {
        "messages": MessageViewSerializer,
        "list": ConversationListSerializer,
    }

    def get_serializer_class(self):
        action = getattr(self, "action", None)
        return self.serializer_class_map.get(action, self.serializer_class)

    def get_queryset(self):
        return (
            self.queryset.filter(participants=self.request.user)
            .select_related(
                "user1",
                "user2",
                "last_message",
                "last_message__sender",
            )
            .prefetch_related(
                "last_message__attachments",
            )
        )

    @action(detail=True, methods=["get"], url_path="messages")
    def messages(self, *args, **kwargs):
        conversation = self.get_object()
        queryset = conversation.messages.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["messages"])
class MessageViewSet(viewsets.ModelViewSet):
    ROOM_PREFIX = "chat_"
    http_method_names = ["post"]
    serializer_class = CreateMessageSerializer
    queryset = Message.objects.order_by("created_at")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class_map = {"create": CreateAttachmentMessageSerializer}
    parser_classes = [parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser]

    def get_serializer_class(self):
        action = getattr(self, "action")
        return self.serializer_class_map.get(action, self.serializer_class)

    def get_queryset(self):
        return self.queryset.filter(sender=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        receiver: User = serializer.validated_data["receiver_id"]

        conversation = (
            ConversationService.get_conversation(
                conversation_id=request.data.get("conversation_id"),
                sender=request.user,
                receiver=receiver,
            )
            if request.data.get("conversation_id")
            else ConversationService.get_or_create_conversation(
                sender=request.user, receiver=receiver
            )
        )

        attachments = [
            Attachment(media=file) for file in serializer.validated_data["attachments"]
        ]

        message = Message.objects.create(
            text=serializer.validated_data["text"],
            conversation=conversation,
            sender=request.user,
            type=Message.MessageType.MEDIA,
        )

        message.attachments.add(*Attachment.objects.bulk_create(attachments))

        conversation.last_message_at = timezone.now()
        conversation.last_message = message
        conversation.save(update_fields=["last_message_at", "last_message"])

        response = MessageViewSerializer(message, context={"request": request}).data

        channel_layer = get_channel_layer()

        for user_id in (request.user.id, receiver.id):
            async_to_sync(channel_layer.group_send)(
                f"{self.ROOM_PREFIX}{user_id}",
                {
                    "type": "chat.message",
                    "data": {"event_type": "chat.message", **response},
                },
            )

        return Response(response, status=status.HTTP_201_CREATED)
