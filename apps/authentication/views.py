from django.db import transaction
from django.contrib.auth import get_user_model

from drf_spectacular.utils import extend_schema

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, status, permissions

from rest_framework_simplejwt.serializers import TokenBlacklistSerializer


from apps.authentication.services import (
    register_user,
    forget_password,
    create_password_secret,
    validate_password_reset_otp,
    validate_password_reset_secret,
    validate_account_activation_otp,
)
from apps.authentication.serializers import (
    TokenSerializer,
    SecretSerializer,
    RefreshTokenSerializer,
    PasswordResetSerializer,
    TokenResponseSerializer,
    ForgetPasswordSerializer,
    ChangePasswordSerializer,
    UserRegistrationSerializer,
    AccountActivationSerializer,
    VerifyPasswordResetSerializer,
)

User = get_user_model()


@extend_schema(tags=["authentication"])
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = []
    serializer_class_map = {
        "token": TokenSerializer,
        "reset": PasswordResetSerializer,
        "refresh": RefreshTokenSerializer,
        "logout": TokenBlacklistSerializer,
        "forget": ForgetPasswordSerializer,
        "password": ChangePasswordSerializer,
        "registration": UserRegistrationSerializer,
        "verify_reset": VerifyPasswordResetSerializer,
        "account_activation": AccountActivationSerializer,
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

    @extend_schema(
        request=RefreshTokenSerializer, responses={201: TokenResponseSerializer}
    )
    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ValidationError({"detail": str(e)})
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise ValidationError({"detail": str(e)})
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="forget")
    def forget(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        forget_password(serializer=serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=VerifyPasswordResetSerializer,
        responses={201: SecretSerializer},
    )
    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="verify-reset")
    def verify_reset(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        otp = validate_password_reset_otp(serializer=serializer)
        password_secret = create_password_secret(user=otp.user)

        otp.used = True
        otp.save(update_fields=["used"])

        return Response({"secret_key": str(password_secret.id)})

    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="reset")
    def reset(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        secret = validate_password_reset_secret(serializer=serializer)

        user = secret.user

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        secret.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=ChangePasswordSerializer, responses=None)
    @transaction.atomic
    @action(
        detail=False,
        methods=["post"],
        url_path="password",
        permission_classes=[permissions.IsAuthenticated],
    )
    def password(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user

        if not user.check_password(
            raw_password=serializer.validated_data["current_password"]
        ):
            raise ValidationError(
                {"password": ["Your provided current password is wrong"]}
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(status=status.HTTP_204_NO_CONTENT)
