from django.urls import path

from apps.chat.consumers import AuthenticatedGlobalSocketConsumer

websocket_urlpatterns = [
    path("socket/connect/", AuthenticatedGlobalSocketConsumer.as_asgi(), name="chat-socket"),
]
