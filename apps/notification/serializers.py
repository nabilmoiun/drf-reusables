from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

from apps.notification.models import Notification, FCMToken


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = ("user",)


@extend_schema_serializer(many=False)
class NotificationListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    total_unseen = serializers.IntegerField()
    results = NotificationSerializer(many=True)


class FCMTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = FCMToken
        exclude = ("user",)


class FCMTokenCreateSerializer(serializers.Serializer):
    token = serializers.CharField()


class SuccessNotificationSerializer(serializers.Serializer):
    detail = serializers.CharField()

