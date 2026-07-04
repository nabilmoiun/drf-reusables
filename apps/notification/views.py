from drf_spectacular.utils import extend_schema

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status, mixins

from apps.notification.models import Notification, FCMToken

from apps.notification.serializers import (
    FCMTokenSerializer,
    NotificationSerializer,
    FCMTokenCreateSerializer,
    SuccessNotificationSerializer,
    NotificationListResponseSerializer,
)

from apps.notification.services import NotificationService


@extend_schema(tags=["notifications"])
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    queryset = Notification.objects.order_by("-created_at")

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @extend_schema(responses=NotificationListResponseSerializer)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        total_unseen = queryset.filter(is_seen=False).count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)

            paginated_response = self.get_paginated_response(serializer.data)

            data = dict(paginated_response.data)
            data["total_unseen"] = total_unseen

            return Response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "total_unseen": total_unseen,
                "results": serializer.data,
            }
        )

    @extend_schema(request=None, responses={200: SuccessNotificationSerializer})
    @action(
        detail=False, methods=["post"], serializer_class=None, url_path="mark-all-seen"
    )
    def mark_all_seen(self, *args, **kwargs):
        self.get_queryset().filter(is_seen=False).update(is_seen=True)
        return Response(
            {"detail": "Notifications marked seen"}, status=status.HTTP_200_OK
        )


@extend_schema(tags=["fcm"])
class FCMTokenViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    pagination_class = None
    http_method_names = ["post", "get"]
    serializer_class = FCMTokenSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FCMToken.objects.order_by("-created_at")

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return FCMTokenCreateSerializer
        return self.serializer_class

    @extend_schema(responses={201: FCMTokenSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance, _ = FCMToken.objects.update_or_create(
            token=serializer.validated_data["token"],
            defaults={"user": request.user},
        )
        serializer = FCMTokenSerializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(request=None, responses=SuccessNotificationSerializer)
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="test",
    )
    def test(self, *args, **kwargs):

        NotificationService.send_push_notification(
            user=self.request.user,
            title="Test Firebase Notification",
            text="Firebase Test Notification",
        )
        return Response(
            {"detail": "Notification sent to user"},
            status=status.HTTP_200_OK,
        )
