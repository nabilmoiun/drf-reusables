from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password

from apps.authentication.models import AccountVerificationOTP

from rest_framework import serializers


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

