from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    background_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_category = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
        )

    class Meta:
        verbose_name_plural = 'categories'
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='unique_category_name_owner')
        ]

    def save(self, *args, **kwargs):
        if self.parent_category is not None and self.parent_category.id == self.id:
            raise ValidationError('Category cannot be its own parent')
        return super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
