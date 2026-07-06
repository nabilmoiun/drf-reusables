from django.contrib import admin

from apps.category.models import Category

from apps.common.admin import BaseAdmin


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ["__str__", "is_active"]

