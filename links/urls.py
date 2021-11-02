from django.urls import path

from .views import (
    LinkListView,
    LinkDetailView,
)

urlpatterns = [
    path("links", LinkListView.as_view(), name="links"),
    path("links/<int:pk>", LinkDetailView.as_view(), name="link"),
]
