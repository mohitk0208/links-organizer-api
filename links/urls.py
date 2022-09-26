from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LinksViewSet

router = DefaultRouter()
router.register(r"links", LinksViewSet, basename="links")

urlpatterns = router.urls
