from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model


User = get_user_model()


class UserService:
    @classmethod
    def get_user_by_id(cls, user_id: str) -> User:
        return User.objects.get(id=user_id)
    
    @classmethod
    def get_active_user_by_id(cls, user_id: str) -> User:
        user = User.objects.filter(id=user_id, is_active=True).first()
        return user
