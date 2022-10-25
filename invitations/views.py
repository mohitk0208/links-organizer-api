from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from categories.models import Category, CategoryAccess
from links_organizer_api.utils.mixins import GetSerializerClassMixin
from links_organizer_api.utils.serializers import EmptySerializer

from .models import CategoryInvitation
from .serializers import (
    CategoryInvitationReceiverSerializer,
    CategoryInvitationSenderSerializer,
)


class CategoryInvitationSenderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CategoryInvitationSenderSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CategoryInvitation.objects.none()

        return CategoryInvitation.objects.filter(sender=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def perform_destroy(self, instance):
        if instance.is_accepted is not None:
            raise ValidationError({"is_accepted": ("Invitation must not be accepted or declined to be deleted.")})

        instance.delete()



class CategoryInvitationReceiverViewSet(
    GetSerializerClassMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CategoryInvitationReceiverSerializer
    serializer_action_classes = {
        "accept": EmptySerializer,
        "reject": EmptySerializer
    }

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CategoryInvitation.objects.none()

        return CategoryInvitation.objects.filter(receiver=self.request.user)


    @swagger_auto_schema(
        operation_summary="Accept a category invitation",
        responses={
            200: "",
        },
    )
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Accept invitation"""
        invitation = self.get_object()

        # invitation already responded
        if invitation.is_accepted is not None:
            raise ValidationError({"detail": "invitation already responded."})

        # create a category access
        category_access = CategoryAccess.objects.create(user=invitation.receiver, category=invitation.category, level=invitation.access_level)
        category_access.save()

        invitation.is_accepted = True
        invitation.save()

        return Response(status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="Reject a category invitation", responses={200: ""}
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject invitation"""
        invitation = self.get_object()
        if invitation.is_accepted is not None:
            raise ValidationError("Already responded to invitation")

        invitation.is_accepted = False
        invitation.save()

        return Response(status=status.HTTP_200_OK)



# class CategoryInvitationViewSet(BaseCategoryInvitationViewSet):

#     serializer_class = CategoryInvitationListCreateSerializer
#     serializer_action_classes = {
#         "destroy": CategoryInvitationDetailSerializer,
#         "accept": EmptySerializer,
#         "reject": EmptySerializer,
#     }
#     filter_backends = (
#         DjangoFilterBackend,
#         OrderingFilter,
#     )

#     def get_queryset(self):
#         if self.action in ["destroy", "sent_invitations"]:
#             return CategoryInvitation.objects.filter(sender=self.request.user)

#         return CategoryInvitation.objects.filter(receiver=self.request.user)

#     def perform_create(self, serializer):
#         # Check if the requesting user is the owner of the category
#         try:
#             obj = Category.objects.get(
#                 owner=self.request.user.id, id=self.request.data["category"]
#             )
#         except Category.DoesNotExist:
#             raise ValidationError("Category does not exist")

#         # Check if the sender and the receiver are not the same
#         if self.request.user.id == self.request.data["receiver"]:
#             raise ValidationError("You can't invite yourself")

#         serializer.save(sender=self.request.user)

#     def perform_destroy(self, instance):
#         if instance.is_accepted != None:
#             raise ValidationError("User has already responded this invitation.")
#         instance.delete()

#     @swagger_auto_schema(
#         operation_summary="Accept a category invitation",
#         responses={
#             200: "",
#         },
#     )
#     @action(detail=True, methods=["post"])
#     def accept(self, request, pk=None):
#         """Accept invitation"""
#         invitation = self.get_object()
#         if invitation.is_accepted is not None:
#             raise ValidationError("Already responded to invitation")

#         invitation.is_accepted = True
#         invitation_category = Category.objects.get(id=invitation.category.id)
#         invitation_category.shared_users.add(invitation.receiver)
#         invitation_category.save()
#         invitation.save()

#         return Response(status=status.HTTP_200_OK)

#     @swagger_auto_schema(
#         operation_summary="Reject a category invitation", responses={200: ""}
#     )
#     @action(detail=True, methods=["post"])
#     def reject(self, request, pk=None):
#         """Reject invitation"""
#         invitation = self.get_object()
#         if invitation.is_accepted is not None:
#             raise ValidationError("Already responded to invitation")

#         invitation.is_accepted = False
#         invitation.save()

#         return Response(status=status.HTTP_200_OK)

#     @action(detail=False, methods=["get"])
#     def sent_invitations(self, request, *args, **kwargs):
#         """Get all sent invitations"""
#         return self.list(request, *args, **kwargs)
