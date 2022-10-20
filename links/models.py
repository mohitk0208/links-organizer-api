from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Link(models.Model):
    url = models.URLField(max_length=200)
    description = models.TextField(max_length=300, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE)
    tags = models.ManyToManyField('tags.Tag', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['url', 'owner'], name='unique_link_owner')
        ]

    def clean(self, *args, **kwargs):
        if self.category.owner != self.owner:
            raise ValidationError({"category": ["category does not exist."]})

        super().clean(*args, **kwargs)


    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

    def get_category(self):
        return self.category

    def __str__(self):
        return self.url
