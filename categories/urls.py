from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CategoryAccessViewset, CategoryViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"category_access", CategoryAccessViewset, basename="category_access")


urlpatterns = router.urls
