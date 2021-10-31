import re

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r"^(?=.{4,15}$)(?![_])(?!.*[_]{2})[a-z0-9_]+(?<![_])$"
    message = _(
        "Username must be 4 to 15 characters long. "
        "It may only contain lowercase alphabets, numbers and underscores. "
        "It shouldn't start or end with underscores. "
        "It shouldn't contain consecutive underscores"
    )
    flags = re.ASCII


class PasswordValidator(validators.RegexValidator):
    regex = r"^(?=.{8,32}$)(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=]).*$"
    message = _(
        "Password must be 8 to 32 characters long. "
        "It must contain at least one uppercase letter, "
        "one lowercase letter, one number and one special character."
    )
    flags = 0


def avatar_validator(value):
    if not value.startswith("https://avatars.dicebear.com/api/"):
        raise ValidationError(
            _("Enter a valid DiceBear avatar url"),
            "invalid",
        )
