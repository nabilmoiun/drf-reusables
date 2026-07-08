from rest_framework import serializers

from apps.rbac.models import Permission, Role


class PermissionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        exclude = ("created_at", "updated_at")


class RoleCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        exclude = ("created_at", "updated_at", "permissions")


class RoleUpdateSerializer(RoleCreateSerializer): ...


class RoleViewSerializer(serializers.ModelSerializer):

    permissions = PermissionViewSerializer(read_only=True, many=True)

    class Meta:
        model = Role
        exclude = ("created_at", "updated_at")


class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ("created_at", "updated_at", "permissions")
