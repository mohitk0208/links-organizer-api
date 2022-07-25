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
        "tags",
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
        return Link.objects.filter(owner=self.request.user).prefetch_related("tags")

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except IntegrityError:
            raise ValidationError({"url": ["This URL is already in use."]})


# class LinkListView(ListCreateAPIView):
#     """
#     List all links or create a new link.
#     """

#     serializer_class = LinkSerializer

#     def get_queryset(self):
#         return Link.objects.filter(owner=self.request.user).prefetch_related("tags")

#     ordering = ("-created_at",)
#     filter_fields = (
#         "category",
#         "tags",
#     )
#     search_fields = (
#         "description",
#         "url",
#     )
#     ordering_fields = (
#         "created_at",
#         "updated_at",
#     )

#     def perform_create(self, serializer):
#         try:
#             serializer.save(owner=self.request.user)
#         except IntegrityError:
#             raise ValidationError({"url": ["This URL is already in use."]})

#     @swagger_auto_schema(
#         tags=("links",),
#         operation_summary="List all links",
#         responses={
#             200: LinkSerializer(many=True),
#             401: "Unauthorized",
#             404: "Not found",
#         },
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

#     @swagger_auto_schema(
#         tags=("links",),
#         operation_summary="Create a new link",
#         request_body=LinkSerializer,
#         responses={
#             201: LinkSerializer,
#             400: "Bad request",
#             401: "Unauthorized",
#             404: "Not found",
#         },
#     )
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)


# class LinkDetailView(RetrieveUpdateDestroyAPIView):
#     """
#     Retrieve, update or delete a link instance.
#     """

#     serializer_class = LinkSerializer

#     def get_queryset(self):
#         return Link.objects.filter(owner=self.request.user)

#     @swagger_auto_schema(
#         tags=("links",),
#         operation_summary="Retrieve a link",
#         responses={
#             200: LinkSerializer,
#             401: "Unauthorized",
#             404: "Not found",
#         },
#     )
#     def get(self, request, pk: int, *args, **kwargs):
#         return super().get(request, pk, *args, **kwargs)

#     @swagger_auto_schema(
#         tags=("links",),
#         operation_summary="replace a link",
#         request_body=LinkSerializer,
#         responses={
#             200: LinkSerializer,
#             400: "Bad request",
#             401: "Unauthorized",
#             404: "Not found",
#         },
#     )
#     def put(self, request, *args, **kwargs):
#         return super().put(request, *args, **kwargs)

#     @swagger_auto_schema(
#         tags=("links",),
#         operation_summary="update a link",
#         request_body=LinkSerializer,
#         responses={
#             200: LinkSerializer,
#             400: "Bad request",
#             401: "Unauthorized",
#             404: "Not found",
#         },
#     )
#     def patch(self, request, *args, **kwargs):
#         return super().patch(request, *args, **kwargs)

#     @swagger_auto_schema(
#         tags=("links",),
#         operation_summary="Delete a link",
#         responses={
#             204: "No content",
#             401: "Unauthorized",
#             404: "Not found",
#         },
#     )
#     def delete(self, request, *args, **kwargs):
#         return super().delete(request, *args, **kwargs)
