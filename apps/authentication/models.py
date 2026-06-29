from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.common.models import TimeStampedUUIDModel


class BaseOTPModel(TimeStampedUUIDModel):
    code = models.CharField(max_length=6)
    used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        abstract = True


class AccountVerificationOTP(BaseOTPModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "account_verification_otps"
        verbose_name = "Account Verification OTP"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self._state.adding:
            expiry_seconds = getattr(settings, "OTP_EXPIRY_SECONDS", 60 * 15)
            self.expired_at = timezone.now() + timedelta(seconds=expiry_seconds)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.email} - {self.code}"
    
    

class PasswordResetOTP(BaseOTPModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "password_reset_otps"
        verbose_name = "Password Reset OTP"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self._state.adding:
            expiry_seconds = getattr(settings, "OTP_EXPIRY_SECONDS")
            self.expired_at = timezone.now() + timedelta(seconds=expiry_seconds)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.code}"
    

class PasswordResetSecret(TimeStampedUUIDModel):
    otp = models.OneToOneField(PasswordResetOTP, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "password_reset_secrets"
        verbose_name = "Password Reset Secret"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self._state.adding:
            expiry_seconds = getattr(settings, "OTP_EXPIRY_SECONDS")
            self.expired_at = timezone.now() + timedelta(seconds=expiry_seconds)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)
