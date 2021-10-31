# from django.conf import settings
from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.core.validators import EmailValidator
# from django.shortcuts import get_object_or_404
# from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# from rest_framework import status
# from rest_framework.exceptions import APIException, ParseError
# from rest_framework.permissions import AllowAny
# from rest_framework.request import Request
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.token_blacklist.models import (
#     BlacklistedToken,
#     OutstandingToken,
# )
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .models import User
from .serializers import (
    # UserSerializer,
    # PublicUserSerializer,
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
    TokenVerifyResponseSerializer,
)

# from .validators import UsernameValidator


UserModel: User = get_user_model()

# Create your views here.


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        tags=("auth",),
        security=[],
        operation_summary="Obtain token pair",
        responses={
            200: TokenObtainPairResponseSerializer,
            400: "Bad request",
            401: "Unauthorized",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        tags=("auth",),
        security=[],
        operation_id="accounts_login_refresh",
        operation_summary="Refresh access token",
        responses={
            200: TokenRefreshResponseSerializer,
            400: "Bad request",
            401: "Unauthorized",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class DecoratedTokenVerifyView(TokenVerifyView):
    @swagger_auto_schema(
        tags=("auth",),
        security=[],
        operation_id="accounts_login_verify",
        operation_summary="Verify token",
        responses={
            200: TokenVerifyResponseSerializer,
            400: "Bad request",
            401: "Unauthorized",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
