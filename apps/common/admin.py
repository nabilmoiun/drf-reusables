from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))

        for field_name in ("id", "created_at", "updated_at"):
            if hasattr(self.model, field_name):
                fields.append(field_name)

        return tuple(fields)
