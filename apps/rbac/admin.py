from django.contrib import admin

from apps.rbac.models import Permission, Role

from apps.common.admin import BaseAdmin


@admin.register(Permission)
class PermissionAdmin(BaseAdmin):
    list_display = ["__str__"]


@admin.register(Role)
class RoleAdmin(BaseAdmin):
    list_display = ["__str__"]


