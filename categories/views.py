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

    def perform_destroy(self, instance):
        # if instance.category.owner.id != self.request.user.id:
            # raise ValidationError({"detail": ("No such shared user.")})


        instance.delete()




# class CategoryAccessViewset(mixins.UpdateModelMixin, viewsets.GenericViewSet):
#     serializer_class = CategoryAccessSerializer
#     queryset = CategoryAccess.objects.all()

#     def perform_update(self, serializer):
#         # check if the requesting user is the owner the Category
#         try:
#             category = Category.objects.get(
#                 id=serializer.data["category"], owner=self.request.user.id
#             )
#         except Category.DoesNotExist:
#             return

# @swagger_auto_schema(
#     operation_summary="Change the permission of a specific shared user",
#     request_body=CategoryAccessModificationSerializer,
#     responses={200: ""},
# )
# @action(detail=True, methods=["post"])
# def change_role(self, request, pk=None):
#     """Change the permission of a shared user"""

#     try:
#         category = Category.objects.get(id=pk, owner=request.user)
#     except Category.DoesNotExist:
#         return Response(None, status=status.HTTP_404_NOT_FOUND)

#     try:
#         accessObj = category.shared_users.through.objects.get(
#             category_id=pk, user_id=request.data["shared_user_id"]
#         )
#         accessObj.level = request.data["level"]
#         accessObj.save()

#     except CategoryAccess.DoesNotExist:
#         return ValidationError(
#             "Provided shared user does not have access to the category"
#         )

#     return Response(None, status=status.HTTP_200_OK)
