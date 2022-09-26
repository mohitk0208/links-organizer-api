from django.urls import path

from .views import (
    DecoratedTokenObtainPairView,
    DecoratedTokenRefreshView,
    DecoratedTokenVerifyView,
    PublicUserProfileView,
    UserExistsView,
    UserListView,
    UserProfileView,
    UserRegisterView,
)

urlpatterns = [
  # JWT
  path("login", DecoratedTokenObtainPairView.as_view(), name="login"),
  path("login/refresh", DecoratedTokenRefreshView.as_view(), name="token_refresh"),
  path("login/verify", DecoratedTokenVerifyView.as_view(), name="token_verify"),
  # Users
  path("users", UserRegisterView.as_view(), name="signup"),
  path("users/search", UserListView.as_view(), name="users_search"),
  path("user/profile", UserProfileView.as_view(), name="user_profile"),
  path("user/<int:pk>", PublicUserProfileView.as_view(), name="user_public"),
  path("user/exists", UserExistsView.as_view(), name="user_exists"),
]
