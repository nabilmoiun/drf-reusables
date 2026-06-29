from django.contrib.auth.models import BaseUserManager


class UserManger(BaseUserManager):
    use_in_migrations = True

    def create_user(self, first_name, last_name, email, password=None, **extra_kwargs):
        if not email:
            raise ValueError("The email must be set")

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email),
            **extra_kwargs
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, last_name, email, password, **extra_kwargs):
        if not password:
            raise ValueError("The password must be set")
        extra_kwargs.update({"is_active": True, "is_staff": True, "is_superuser": True})
        return self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            **extra_kwargs
        )
