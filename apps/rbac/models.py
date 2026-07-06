from django.db import models

from apps.common.models import TimeStampedUUIDModel


class Permission(TimeStampedUUIDModel):
    code = models.CharField(max_length=150, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=150)

    class Meta:
        db_table = "permissions"
        verbose_name = "Permission"
        ordering = ["name"]

    def __str__(self):
        return self.code


class Role(TimeStampedUUIDModel):
    permissions = models.ManyToManyField(Permission, blank=True)
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, max_length=150)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        ordering = ["name"]

    def __str__(self):
        return self.name

