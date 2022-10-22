from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from categories.models import AccessLevel


# Create your models here.
class CategoryInvitation(models.Model):
    """
    Models to store category invitation so that a user can be given access to the category.
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver"
    )
    category = models.ForeignKey("categories.Category", on_delete=models.CASCADE)
    note = models.TextField(default="")
    access_level = models.IntegerField(choices=AccessLevel.choices, default=AccessLevel.READ_ONLY)
    is_accepted = models.BooleanField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "category_invitations"
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver", "category"],
                name="unique_category_invitation",
            ),
            models.CheckConstraint(
                check=~models.Q(sender=models.F("receiver")), name="sender_not_receiver"
            ),
        ]

    def clean(self, *args, **kwargs):
        if self.category.owner != self.sender:
            raise ValidationError({"detail": "Category does not exist"})

        super(CategoryInvitation, self).clean(*args, **kwargs)


    def save(self, *args, **kwargs):
        self.full_clean()

        super(CategoryInvitation, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.sender} -> {self.receiver} for the Category {self.category}"
