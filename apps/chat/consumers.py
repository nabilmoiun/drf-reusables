from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class AuthenticatedGlobalSocketConsumer(JsonWebsocketConsumer):
    def connect(self):
        user_id = self.scope["user_id"]

        if not user_id:
            self.close()
            return
        
        self.accept()
    
    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive(self, text_data = None, bytes_data = None, **kwargs):
        return super().receive(text_data, bytes_data, **kwargs)
    
    def send_json(self, content, close = False):
        return super().send_json(content, close)
    
    def send(self, text_data = None, bytes_data = None, close = False):
        return super().send(text_data, bytes_data, close)
    
