from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryInvitationReceiverViewSet, CategoryInvitationSenderViewSet

router = DefaultRouter()
router.register(
    r"sender_category_invitations", CategoryInvitationSenderViewSet, basename="sender_category_invitations",
)
router.register(r"receiver_category_invitations", CategoryInvitationReceiverViewSet, basename="receiver_category_invitations")

urlpatterns = router.urls
