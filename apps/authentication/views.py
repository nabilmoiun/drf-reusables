from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.authentication.services import register_user
from apps.authentication.serializers import UserRegistrationSerializer


User = get_user_model()


@extend_schema(tags=["authentication"])
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class_map = {"registration": UserRegistrationSerializer}

    def get_serializer_class(self):
        action = getattr(self, "action", None)
        return self.serializer_class_map[action]

    @extend_schema(responses={201: UserRegistrationSerializer})
    @transaction.atomic
    @action(detail=False, methods=["post"], url_name="registration")
    def registration(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        
        register_user(serializer=serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
