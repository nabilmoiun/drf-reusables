from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UpperLowerCasePasswordValidator:
    def validate(self, password, user=None):
        if not any(c.islower() for c in password) or not any(c.isupper() for c in password):
            raise ValidationError(
                _("Password must contain at least one uppercase and one lowercase letter."),
                code="password_no_mixed_case",
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase and one lowercase letter.")
    