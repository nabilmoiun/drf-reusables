from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class SocketService:
    @classmethod
    def build_socket_response(
        cls,
        success: bool,
        error: str | None,
        data: dict | None = None,
        event_type: str = "chat.message",
    ):
        return {
            "success": success,
            "error": error,
            "data": data or {},
            "event_type": event_type,
        }
    
    @classmethod
    def broadcast(cls, room_ids: list, handler: str, data: dict):
        channel_layer = get_channel_layer()
        for room in room_ids:
            async_to_sync(channel_layer.group_send)(
                    room,
                    {
                        "type": handler,
                        "data": data,
                    },
                )
