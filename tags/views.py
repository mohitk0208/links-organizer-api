from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVector
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from links_organizer_api.utils.paginations import CustomLimitOffsetPagination

from .models import Tag
from .serializers import TagDetailSerializer

UserModel = get_user_model()


class TagListView(ListCreateAPIView):

    pagination_class = CustomLimitOffsetPagination
    serializer_class = TagDetailSerializer

    def get_queryset(self):
        tags = Tag.objects.all()

        tag_ids = self.request.query_params.get("ids", None)
        if tag_ids:
            return tags.filter(id__in=tag_ids.split(","))

        tag_name = self.request.query_params.get("name", None)
        if tag_name:
            vector = SearchVector("name")  # + SearchVector("description")
            tags = tags.annotate(search=vector).filter(search__icontains=tag_name)
        return tags

    @swagger_auto_schema(
        tags=("tags",),
        operation_summary="Get tags",
        manual_parameters=(
            openapi.Parameter(
                "name",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search tags by name",
            ),
            openapi.Parameter(
                "ids",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Get tags by id",
            ),
        ),
        responses={
            200: TagDetailSerializer(many=True),
            401: "Unauthorized.",
            404: "Not Found.",
        },
    )
    def get(self, request: Request) -> Response:
        return super().get(request)

    @swagger_auto_schema(
        tags=("tags",),
        operation_summary="Create a new tag",
        responses={
            201: TagDetailSerializer,
            400: "Bad request.",
            401: "Unauthorized.",
        },
    )
    def post(self, request: Request) -> Response:
        return super().post(request)


class TagDetailView(RetrieveAPIView):
    serializer_class = TagDetailSerializer
    queryset = Tag.objects.all()

    @swagger_auto_schema(
        tags=("tags",),
        operation_summary="Get tag details",
        responses={
            200: TagDetailSerializer,
            401: "Unauthorized.",
            404: "Not found.",
        },
    )
    def get(self, request: Request, pk: int) -> Response:
        return super().get(request, pk)
