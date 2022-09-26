from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AccessLevel(models.IntegerChoices):
    ADMIN = 100
    READ_WRITE = 200
    READ_ONLY = 300


class Category(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    background_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    shared_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="categories.CategoryAccess",
        through_fields=("category", "user"),
        related_name="shared_categories",
    )

    class Meta:
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "owner"], name="unique_category_name_owner"
            )
        ]

    def save(self, *args, **kwargs):
        if self.parent_category is not None and self.parent_category.id == self.id:
            raise ValidationError("Category cannot be its own parent")
        return super(Category, self).save(*args, **kwargs)

    def get_access_level(self, user_id: int):
        try:
            access = self.shared_users.through.objects.get(
                category_id=self.id, user_id=user_id
            )
        except CategoryAccess.DoesNotExist:
            return None
        return access.level

    def get_category(self):
        return self

    def __str__(self) -> str:
        return self.name


class CategoryAccess(models.Model):
    category = models.ForeignKey(Category, db_index=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    level = models.IntegerField(
        choices=AccessLevel.choices, default=AccessLevel.READ_ONLY
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category", "user"], name="unique_category_access_through"
            )
        ]
