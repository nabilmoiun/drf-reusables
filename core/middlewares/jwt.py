from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

jwt_auth = JWTAuthentication()


@database_sync_to_async
def authenticate_user(token):
    try:
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)

        if not user.is_active:
            return None

        return user

    except (InvalidToken, TokenError, User.DoesNotExist):
        return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):

        headers = {
            k.decode().lower(): v.decode()
            for k, v in scope.get("headers", [])
        }

        params = parse_qs(
            scope.get("query_string", b"").decode()
        )

        token = None

        auth_header = headers.get("authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        if token is None:
            token = params.get("token", [None])[0]

        scope["user"] = (
            await authenticate_user(token)
            if token
            else None
        )

        return await super().__call__(scope, receive, send)
