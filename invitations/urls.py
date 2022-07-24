from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryInvitationViewSet

router = DefaultRouter()
router.register(
    r"category_invitations", CategoryInvitationViewSet, basename="category_invitations"
)

urlpatterns = router.urls
