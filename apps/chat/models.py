from django.db import models
from django.conf import settings


from apps.common.models import TimeStampedUUIDModel


class Conversation(TimeStampedUUIDModel):
    """
    Used for One to One chat between 2 participants

    We shall store user1 and user2 as well for sake of optimizing query performance
    while creating a conversation for the first time.
    """

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
        blank=False,
    )
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="conversations_as_user1",
        on_delete=models.CASCADE,
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="conversations_as_user2",
        on_delete=models.CASCADE,
    )
    last_message_at = models.DateTimeField()
    last_message = models.ForeignKey(
        "Message", related_name="+", null=True, blank=True, on_delete=models.SET_NULL
    )
    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="blocked_conversations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        db_table = "conversations"
        verbose_name = "Conversation"
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"], name="unique_conversation_pair"
            )
        ]

    def __str__(self):
        return str(self.id)

    def get_other_conversation_user(self, auth_user):
        user = self.user2 if self.user1 == auth_user else self.user1
        return user


class Attachment(TimeStampedUUIDModel):
    media = models.FileField(upload_to="chat_attachments")

    class Meta:
        db_table = "attachments"
        verbose_name = "Attachment"

    def __str__(self):
        return str(self.media.url)


class Message(TimeStampedUUIDModel):
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
        return self.sender.full_name
