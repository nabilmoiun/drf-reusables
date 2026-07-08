from rest_framework.exceptions import PermissionDenied

from functools import wraps

from core.permissions.utils import user_has_permission


def required_permission(permission_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = args[1]
            user = request.user
            if not user_has_permission(user=user, code=permission_name):
                raise PermissionDenied(detail="You don't have permission to perform this action", code=403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

