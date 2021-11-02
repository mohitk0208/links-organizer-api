from django.db import models

from .validators import TagNameValidator


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=(TagNameValidator(),),
        help_text=(
            "Tag name must be 1 to 50 characters long. "
            "It may only contain lowercase alphabets, numbers and hyphens. "
            "It shouldn't start or end with hyphens. "
            "It shouldn't contain consecutive hyphens"
        ),
        error_messages={'unique': 'Tag with this name already exists.'}
    )
    description = models.TextField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"T{self.id} - {self.name}"
