from django.contrib import admin

from apps.common.admin import BaseAdmin
from apps.notification.models import Notification, FCMToken


@admin.register(Notification)
class NotificationAdmin(BaseAdmin):
    list_display = [
        "__str__",
        "title",
        "is_seen",
    ]


@admin.register(FCMToken)
class FCMTokenAdmin(BaseAdmin):
    list_display = [
        "__str__",
        "token"
    ]

