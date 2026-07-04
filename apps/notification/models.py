from django.db import models
from django.conf import settings


from apps.common.models import TimeStampedUUIDModel


class Notification(TimeStampedUUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    text = models.TextField()
    is_seen = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications"
        verbose_name = "Notification"
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.user)
    

class FCMToken(TimeStampedUUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="fcm_tokens", on_delete=models.CASCADE
    )
    token = models.TextField(unique=True, db_index=True)

    class Meta:
        db_table = "fcm_tokens"
        verbose_name = "FCM Token"

    def __str__(self):
        return str(self.user)
