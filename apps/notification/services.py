import json
import logging
import requests
from typing import List
from google.oauth2 import service_account

from google.auth.transport.requests import Request


from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.notification.models import Notification

User = get_user_model()

logger = logging.getLogger(__name__)


class FCMPushNotification:
    FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"

    def _get_access_token(self):
        token = cache.get("fcm_access_token")
        if token:
            return token

        credentials = service_account.Credentials.from_service_account_file(
            settings.FCM_SERVICE_ACCOUNT_FILE,
            scopes=[self.FCM_SCOPE],
        )

        credentials.refresh(Request())

        token = credentials.token

        # cache for 55 minutes (safe buffer under 1h expiry)
        cache.set("fcm_access_token", token, timeout=55 * 60)

        return token

    def send(self, token: str, title: str, body: str, data: dict = None):
        access_token = self._get_access_token()

        project_id = settings.FIREBASE_PROJECT_ID

        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "data": {**(data or {})},
                "android": {
                    "priority": "high",
                },
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code != 200:
            return {"error": response.text}

        return response.json()


class NotificationService:

    push_service_class = FCMPushNotification

    @classmethod
    def create_notification(cls, *, user: User, title: str, text: str) -> Notification:
        instance = Notification.objects.create(user=user, title=title, text=text)
        return instance

    @classmethod
    def send_push_notification(cls, user, title: str, text: str, **extra_data):

        tokens = list(user.fcm_tokens.values_list("token", flat=True))
        if not tokens:
            return

        push_service = cls.push_service_class()

        for token in tokens:
            try:
                response = push_service.send(
                    token=token,
                    title=title,
                    body=text,
                    data=extra_data,
                )

                print("Response from firebase: ---\n", response)

                if response and isinstance(response, dict):
                    error = response.get("error", {})

                    if isinstance(error, str):
                        try:
                            error = json.loads(error)
                        except Exception:
                            error = {}

                    status = error.get("status")

                    if status in ("UNREGISTERED", "INVALID_ARGUMENT"):
                        user.fcm_tokens.filter(token=token).delete()

            except Exception as e:
                logger.exception(f"FCM push failed for user={user.id}: {str(e)}")
