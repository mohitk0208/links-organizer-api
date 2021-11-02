from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin

from .models import Link


class LinkAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_display = ('url', 'description', 'owner', 'category', 'created_at', 'updated_at')
    list_display_links = list_display
    list_filter = ('category', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    search_fields = ('url', 'description', 'owner__username', 'owner__email')
    ordering = ('-created_at',)
    fieldsets = (
        (
            None, {
                'fields': ('id', 'owner', 'url', 'category', 'description', 'tags')
            }
        ),
        (
            'Metadata', {
                'fields': ('created_at', 'updated_at')
            }
        )
    )


admin.site.register(Link, LinkAdmin)
