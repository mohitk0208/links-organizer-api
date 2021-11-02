from django.urls import path

from .views import (
    TagDetailView,
    TagListView,
)

urlpatterns = [
    path("tags", TagListView.as_view(), name="tags"),
    path("tags/<int:pk>", TagDetailView.as_view(), name="tag"),
]
