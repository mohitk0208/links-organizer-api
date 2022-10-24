from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Link
from .serializers import LinkSerializer


class LinksViewSet(viewsets.ModelViewSet):
    serializer_class = LinkSerializer
    ordering = ("-created_at",)
    filter_fields = (
        "category",
        # "tags",
    )
    search_fields = (
        "description",
        "url",
    )
    ordering_fields = (
        "created_at",
        "updated_at",
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Link.objects.none()

        if self.action != "list":
            return Link.objects.filter(owner=self.request.user).prefetch_related("tags")

        ids = self.request.query_params.get("tags", None)
        if ids:
            ids = ids.split(",")
            links = Link.objects.filter(owner=self.request.user).prefetch_related(
                "tags"
            )
            for id_ in ids:
                links = links.filter(tags__id=id_)
            return links

        return Link.objects.filter(owner=self.request.user).prefetch_related("tags")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
