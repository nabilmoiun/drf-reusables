from urllib.parse import parse_qs
from django.contrib.auth import get_user_model

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

jwt_auth = JWTAuthentication()


@database_sync_to_async
def get_user_id(token):
    try:
        validated_token = jwt_auth.get_validated_token(token)
        return validated_token["user_id"]
    except Exception:
        return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = {
            k.decode("utf-8").lower(): v.decode("utf-8")
            for k, v in scope.get("headers", [])
        }

        query_string = scope.get("query_string") or b""
        query_string = query_string.decode("utf-8", "ignore")
        params = parse_qs(query_string)

        token = None

        auth_header = headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            token = params.get("token", [None])[0]

        scope["user_id"] = await get_user_id(token) if token else None

        return await super().__call__(scope, receive, send)
