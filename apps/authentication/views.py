from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.authentication.services import (
    register_user,
    validate_account_activation_otp,
)
from apps.authentication.serializers import (
    TokenSerializer,
    TokenResponseSerializer,
    UserRegistrationSerializer,
    AccountActivationSerializer,
)

User = get_user_model()


@extend_schema(tags=["authentication"])
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class_map = {
        "registration": UserRegistrationSerializer,
        "account_activation": AccountActivationSerializer,
        "token": TokenSerializer
    }

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

    @extend_schema(
        request=AccountActivationSerializer,
        responses={201: UserRegistrationSerializer},
    )
    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="account-activation")
    def account_activation(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        otp = validate_account_activation_otp(serializer=serializer)
        user = otp.user

        user.is_active = True
        user.save(update_fields=["is_active"])

        otp.delete()

        return Response(
            UserRegistrationSerializer(user).data, status=status.HTTP_201_CREATED
        )
    
    @extend_schema(responses={201: TokenResponseSerializer})
    @action(detail=False, methods=["post"], url_path="token")
    def token(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
