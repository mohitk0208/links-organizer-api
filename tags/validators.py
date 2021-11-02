import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class TagNameValidator(validators.RegexValidator):
    regex = r"^(?=.{1,50}$)(?![-])(?!.*[-]{2})[a-z0-9-]+(?<![-])$"
    message = _(
        "Tag name must be 1 to 50 characters long. "
        "It may only contain lowercase alphabets, numbers and hyphens. "
        "It shouldn't start or end with hyphens. "
        "It shouldn't contain consecutive hyphens"
    )
    flags = re.ASCII
