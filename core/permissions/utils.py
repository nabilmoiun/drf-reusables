def user_has_permission(user, code) -> bool:
    if user.is_superuser:
        return True

    if code is None:
        return True

    return user.roles.filter(
        permissions__code=code
    ).exists()
