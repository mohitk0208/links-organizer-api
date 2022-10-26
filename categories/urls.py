from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryAccessViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"category_access", CategoryAccessViewSet, basename="category_access")


urlpatterns = router.urls
