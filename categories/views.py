from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from links_organizer_api.utils.mixins import GetSerializerClassMixin
from links_organizer_api.utils.serializers import EmptySerializer

from .models import Category, CategoryAccess
from .serializers import CategoryAccessSerializer, CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet, GetSerializerClassMixin):
    serializer_class = CategorySerializer
    ordering = "-created_at"
    filter_fields = ("parent_category",)
    search_fields = ("name", "description")
    ordering_fields = ("created_at", "updated_at", "name")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Category.objects.none()

        return Category.objects.filter(owner=self.request.user).prefetch_related("shared_users")

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except IntegrityError:
            raise ValidationError({"name": ["Category already exists"]})


class CategoryAccessViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
 ):
    serializer_class = CategoryAccessSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CategoryAccess.objects.none()

        return CategoryAccess.objects.all()

    def check_object_permissions(self, request, obj):
        if obj.category.owner != request.user:
            raise PermissionDenied(detail="no privileges to perform this action")


class SharedCategoryViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):

    serializer_class = CategorySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Category.objects.none()


        # shared_categories_id = map(lambda x:x.category.id, CategoryAccess.objects.filter(user=self.request.user))

        # shared_categories = Category.objects.filter(id__in=shared_categories_id)

        # return shared_categories


        return Category.objects.filter(shared_users__id=self.request.user.id)

