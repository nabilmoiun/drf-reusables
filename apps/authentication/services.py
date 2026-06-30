from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from apps.authentication.models import AccountVerificationOTP

from core.services.email import send_user_email
from core.services.otp import generate_random_otp

User = get_user_model()


def delete_unused_account_verification_otp(user: User) -> None:
    AccountVerificationOTP.objects.filter(user=user, used=False).delete()


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


def validate_account_activation_otp(
    serializer: serializers.ModelSerializer,
) -> AccountVerificationOTP:

    qs = AccountVerificationOTP.objects.filter(
        user__email=serializer.validated_data["email"],
        used=False,
        expires_at__gte=timezone.now(),
    ).select_related("user")

    if not qs.exists():
        raise serializers.ValidationError(
            {"detail": ["The otp is invalid or expired"]}
        )

    otp = qs.first()

    if not otp.verify_code(code=serializer.validated_data["code"]):
        raise serializers.ValidationError(
            {"detail": ["The otp is invalid"]}
        )
    return otp
