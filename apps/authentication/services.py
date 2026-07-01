from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.authentication.models import (
    PasswordResetOTP,
    PasswordResetSecret,
    AccountVerificationOTP,
)

from core.services.email import send_user_email
from core.services.otp import generate_random_otp

User = get_user_model()


def delete_unused_account_verification_otp(user: User) -> None:
    AccountVerificationOTP.objects.filter(user=user, used=False).delete()


def delete_unused_password_reset_otp(user: User) -> None:
    PasswordResetOTP.objects.filter(user=user, used=False).delete()


def create_account_verification_otp(user: User, code: str) -> AccountVerificationOTP:
    delete_unused_account_verification_otp(user=user)
    now = timezone.now()
    delta = timedelta(seconds=settings.OTP_EXPIRY_SECONDS)

    otp = AccountVerificationOTP(user=user, expires_at=now + delta)
    otp.set_code(code=code)
    otp.save()
    return otp


def send_account_verification_otp(user: User, code: str) -> None:
    context = {
        "name": user.full_name,
        "code": code,
        "duration": int(getattr(settings, "OTP_EXPIRY_SECONDS")) // 60,
    }
    send_user_email(
        subject="Activate your account",
        to=[user.email],
        template_name=settings.ACCOUNT_ACTIVATION_TEMPLATE,
        context=context,
    )


def create_password_reset_otp(user: User, code: str) -> PasswordResetOTP:
    delete_unused_password_reset_otp(user=user)
    now = timezone.now()
    delta = timedelta(seconds=settings.OTP_EXPIRY_SECONDS)

    otp = PasswordResetOTP(user=user, expires_at=now + delta)
    otp.set_code(code=code)
    otp.save()
    return otp


def send_password_reset_otp(user: User, code: str) -> None:
    context = {
        "name": user.full_name,
        "code": code,
        "duration": int(getattr(settings, "OTP_EXPIRY_SECONDS")) // 60,
    }
    send_user_email(
        subject="Reset your password",
        to=[user.email],
        template_name=settings.PASSWORD_RESET_TEMPLATE,
        context=context,
    )


def create_password_secret(user: User) -> PasswordResetSecret:
    now = timezone.now()
    delta = timedelta(seconds=settings.OTP_EXPIRY_SECONDS)
    PasswordResetSecret.objects.filter(user=user).delete()

    return PasswordResetSecret.objects.create(user=user, expires_at=now + delta)


def validate_account_activation_otp(
    serializer: serializers.ModelSerializer,
) -> AccountVerificationOTP:

    qs = AccountVerificationOTP.objects.filter(
        user__email=serializer.validated_data["email"],
        used=False,
        expires_at__gte=timezone.now(),
    ).select_related("user")

    if not qs.exists():
        raise ValidationError({"detail": "The otp is invalid or expired"})

    otp = qs.first()

    if not otp.verify_code(code=serializer.validated_data["code"]):
        raise ValidationError({"detail": "The otp is invalid"})

    return otp


def validate_password_reset_otp(
    serializer: serializers.ModelSerializer,
) -> PasswordResetOTP:

    qs = PasswordResetOTP.objects.filter(
        user__email=serializer.validated_data["email"],
        used=False,
        expires_at__gte=timezone.now(),
    ).select_related("user")

    if not qs.exists():
        raise ValidationError({"detail": "The otp is invalid or expired"})

    otp = qs.first()

    if not otp.verify_code(code=serializer.validated_data["code"]):
        raise ValidationError({"detail": "The otp is invalid"})
    return otp


def validate_password_reset_secret(
    serializer: serializers.Serializer,
) -> PasswordResetSecret:
    secret = (
        PasswordResetSecret.objects.filter(
            id=serializer.validated_data.get("secret_key"),
            expires_at__gte=timezone.now(),
        )
        .select_related("user")
        .first()
    )

    if not secret:
        raise ValidationError({"detail": "Invalid secret key or expired"})

    return secret


@transaction.atomic
def register_user(serializer: serializers.ModelSerializer) -> User:
    user, _ = User.objects.update_or_create(
        email=serializer.validated_data["email"],
        defaults={
            "first_name": serializer.validated_data["first_name"],
            "last_name": serializer.validated_data["last_name"],
            "password": make_password(serializer.validated_data["password"]),
            "is_active": False,
        },
    )

    code = generate_random_otp(length=6)
    otp = create_account_verification_otp(user=user, code=code)

    try:
        send_account_verification_otp(user=user, code=code)
    except:
        user.delete()
        otp.delete()

    return user


@transaction.atomic
def forget_password(serializer: serializers.ModelSerializer) -> None:
    user = User.objects.get(email=serializer.validated_data.get("email"))
    delete_unused_password_reset_otp(user=user)

    code = generate_random_otp(length=6)
    create_password_reset_otp(user=user, code=code)

    send_password_reset_otp(user=user, code=code)
