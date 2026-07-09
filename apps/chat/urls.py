from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.chat.views import ConversationViewSet, MessageViewSet

router = DefaultRouter()

router.register(
    "chat/conversations", ConversationViewSet, basename="chat-conversations"
)

router.register(
    "chat/messages", MessageViewSet, basename="chat-messages"
)

urlpatterns = [path("", include(router.urls))]
