from django.db import models
from django.conf import settings


from apps.common.models import TimeStampedUUIDModel


class Conversation(TimeStampedUUIDModel):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
        null=False,
        blank=False,
    )
    last_message_at = models.DateTimeField()
    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        db_table = "conversations"
        verbose_name = "Conversation"

    def __str__(self):
        return str(self.id)


class Attachment(TimeStampedUUIDModel):
    media = models.FileField(upload_to="chat_attachments")

    class Meta:
        db_table = "attachments"
        verbose_name = "Attachment"

    def __str__(self):
        return str(self.media.url)


class Messaage(TimeStampedUUIDModel):
    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        MEDIA = "media", "Media"

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    text = models.TextField(null=True)
    attachments = models.ManyToManyField(Attachment, blank=True)
    type = models.CharField(
        max_length=30, choices=MessageType, default=MessageType.TEXT
    )
    is_seen = models.BooleanField(default=False)

    class Meta:
        db_table = "messages"
        verbose_name = "Message"
        ordering = ["created_at"]

    def __str__(self):
        return self.sender
