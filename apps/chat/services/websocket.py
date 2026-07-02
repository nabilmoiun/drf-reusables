class SocketService:
    @classmethod
    async def build_socket_response(
        cls,
        success: bool,
        error: str,
        data: dict | None = None,
        event_type: str = "chat.message",
    ):
        return {
            "success": success,
            "error": error,
            "data": data or {},
            "event_type": event_type,
        }
