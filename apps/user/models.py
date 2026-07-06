import uuid
from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

from apps.rbac.models import Role
from apps.common.models import TimeStampedUUIDModel

from apps.user.managers import UserManger


class User(AbstractBaseUser, PermissionsMixin, TimeStampedUUIDModel):
    roles = models.ManyToManyField(Role, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = UserManger()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "uses"
        verbose_name = "User"

    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        f_name = getattr(self, "first_name")
        l_name = getattr(self, "last_name")

        if f_name and l_name:
            return f"{f_name} {l_name}"
        
        return getattr(self, str(self.USERNAME_FIELD))


