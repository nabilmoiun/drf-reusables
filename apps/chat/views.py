from drf_spectacular.utils import extend_schema

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from apps.chat.models import Conversation
from apps.chat.serializers import ConversationListSerializer, MessageViewSerializer


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
