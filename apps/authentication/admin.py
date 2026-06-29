from django.contrib import admin

from apps.common.admin import BaseAdmin
from apps.authentication.models import (
    PasswordResetOTP,
    PasswordResetSecret,
    AccountVerificationOTP,
)


@admin.register(AccountVerificationOTP)
class AccountVerificationOTPAdmin(BaseAdmin):
    list_display = [
        "__str__",
        "used",
        "created_at",
        "expires_at",
    ]


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(BaseAdmin):
    list_display = [
        "__str__",
        "used",
        "created_at",
        "expires_at",
    ]


@admin.register(PasswordResetSecret)
class PasswordResetSecretAdmin(BaseAdmin):
    list_display = [
        "__str__",
        "created_at",
        "expires_at",
    ]
