from django.urls import path

from .views import (
  DecoratedTokenObtainPairView,
  DecoratedTokenRefreshView,
  DecoratedTokenVerifyView,
)

urlpatterns = [
  # JWT
  path("login", DecoratedTokenObtainPairView.as_view(), name="login"),
  path("login/refresh", DecoratedTokenRefreshView.as_view(), name="token_refresh"),
  path("login/verify", DecoratedTokenVerifyView.as_view(), name="token_verify"),
]