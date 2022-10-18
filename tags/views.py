from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from links_organizer_api.utils.paginations import CustomLimitOffsetPagination

from .models import Tag
from .serializers import TagDetailSerializer

UserModel = get_user_model()


class TagViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TagDetailSerializer
    ordering = "-created_at"
    pagination_class = CustomLimitOffsetPagination
    ordering_fields = ("created_at", "updated_at", "name")

    def get_queryset(self):
        if self.action == "retrieve":
            return Tag.objects.all()

        tag_ids = self.request.query_params.get("ids", None)
        if tag_ids:
            return Tag.objects.filter(id__in=tag_ids.split(","))

        tag_name = self.request.query_params.get("name", None)
        if tag_name:
            vector = SearchVector("name")  # + SearchVector("description")
            return Tag.objects.annotate(search=vector).filter(
                search__icontains=tag_name
            )
        return Tag.objects.all()
