from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from links_organizer_api.utils.mixins import GetSerializerClassMixin
from links_organizer_api.utils.serializers import EmptySerializer

from .models import CategoryInvitation
from .serializers import (
    BasicCategoryInvitationSerializer,
    CategoryInvitationDetailSerializer,
    CategoryInvitationListCreateSerializer,
)


class BaseCategoryInvitationViewSet(
    GetSerializerClassMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryInvitationViewSet(BaseCategoryInvitationViewSet):

    serializer_class = CategoryInvitationListCreateSerializer
    serializer_action_classes = {
        "destroy": CategoryInvitationDetailSerializer,
        "accept": EmptySerializer,
        "reject": EmptySerializer,
    }

    def get_queryset(self):
        if self.action == "destroy":
            return CategoryInvitation.objects.filter(sender=self.request.user)

        return CategoryInvitation.objects.filter(receiver=self.request.user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

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
        invitation.is_accepted = False
        invitation.save()

        return Response(status=status.HTTP_200_OK)
