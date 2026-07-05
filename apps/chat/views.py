from drf_spectacular.utils import extend_schema

from rest_framework import viewsets, permissions

from apps.chat.models import Conversation
from apps.chat.serializers import ConversationListSerializer


@extend_schema(tags=["chat"])
class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationListSerializer
    queryset = Conversation.objects.order_by("last_message_at")
    serializer_class_map = {"list": ConversationListSerializer}

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
