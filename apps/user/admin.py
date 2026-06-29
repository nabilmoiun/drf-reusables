from django.contrib import admin

from apps.user.models import User



class BaseAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))

        for field_name in ("id", "created_at", "updated_at"):
            if hasattr(self.model, field_name):
                fields.append(field_name)

        return tuple(fields)
    

@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = ["__str__", "is_active", "is_staff"]

