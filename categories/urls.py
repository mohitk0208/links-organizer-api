from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryAccessViewSet, CategoryViewSet, SharedCategoryViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"category_access", CategoryAccessViewSet, basename="category_access")
router.register(r"shared_categories", SharedCategoryViewSet, basename="shared_categories")


urlpatterns = router.urls
