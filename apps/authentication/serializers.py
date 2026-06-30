from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
    TokenObtainPairSerializer,
)

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")

    def validate_email(self, value):
        if User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("A user with the email already exists")
        return value


class AccountActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()


class TokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        return super().validate(attrs)


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        return super().validate(attrs)
    

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No active user with the provided email")
        return value
    

class VerifyPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()


class SecretSerializer(serializers.Serializer):
    secret_key = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    secret_key = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])




