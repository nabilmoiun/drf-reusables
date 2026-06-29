from django.contrib import admin
from apps.common.admin import BaseAdmin

from apps.user.models import User


@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = ["__str__", "is_active", "is_staff"]

