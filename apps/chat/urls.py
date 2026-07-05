from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.chat.views import ConversationViewSet

router = DefaultRouter()

router.register(
    "chat/conversations", ConversationViewSet, basename="chat-conversations"
)


urlpatterns = [path("", include(router.urls))]
