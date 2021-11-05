from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

from .serializers import CategorySerializer
from .models import Category


class CategoryListView(ListCreateAPIView):
    """
    List all categories or create a new category
    """

    serializer_class = CategorySerializer
    ordering = ('-created_at')
    filter_fields = ('parent_category',)
    search_fields = ('name', 'description')
    odering_fields = ('created_at', 'updated_at', 'name')

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except IntegrityError:
            raise ValidationError({"name": ["Category already exists"]})

    @swagger_auto_schema(
        tags=('categories',),
        operation_summary='get all categories',
        responses={
            200: CategorySerializer(many=True),
            401: 'Unauthorized',
        }
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=('categories',),
        operation_summary='create a new category',
        responses={
          201: CategorySerializer,
          401: 'Unauthorized',
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)


class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category instance.
    """

    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)

    @swagger_auto_schema(
        tags=('categories',),
        operation_summary='get a category',
        responses={
            200: CategorySerializer,
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
    def get(self, request: Request, pk: int, *args, **kwargs) -> Response:
        return super().get(request, pk, *args, **kwargs)

    @swagger_auto_schema(
        tags=('categories',),
        operation_summary='replace category',
        responses={
            200: CategorySerializer,
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
    def put(self, request: Request, *args, **kwargs) -> Response:
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=('categories',),
        operation_summary='update a category',
        responses={
            200: CategorySerializer,
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
    def patch(self, request: Request, *args, **kwargs) -> Response:
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=('categories',),
        operation_summary='delete a category',
        responses={
            204: 'No content',
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        return super().delete(request, *args, **kwargs)
