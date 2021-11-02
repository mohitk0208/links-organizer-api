from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin

from .models import Category


class CategoryAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'parent_category', 'owner', 'created_at', 'updated_at')
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")

    # TODO handle validation errors


admin.site.register(Category, CategoryAdmin)
