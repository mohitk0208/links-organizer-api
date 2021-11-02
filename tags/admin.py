from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin

from .models import Tag


class TagAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "name",
                    "description",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


admin.site.register(Tag, TagAdmin)