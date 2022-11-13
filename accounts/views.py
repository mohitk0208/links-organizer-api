# from django.conf import settings
from django.contrib.auth import get_user_model

# from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import EmailValidator
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView

# from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# from rest_framework_simplejwt.token_blacklist.models import (
#     BlacklistedToken,
#     OutstandingToken,
# )
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .models import User
from .serializers import (
    PublicUserSerializer,
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
    TokenVerifyResponseSerializer,
    UserSerializer,
)
from .validators import UsernameValidator

UserModel: User = get_user_model()


class UserListView(ListAPIView):
    """"List the users"""

    serializer_class = PublicUserSerializer
    ordering = ('first_name', 'email', 'username')
    filter_fields = ('email', 'username')
    search_fields = ('username', 'email')
    ordering_fields = ('first_name', 'email', 'username')

    def get_queryset(self):
        return UserModel.objects.all()




class UserRegisterView(APIView):
    """Register a new user"""

    authentication_classes = ()
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=("users", "auth"),
        security=[],
        operation_summary="Register a new user",
        request_body=UserSerializer,
        responses={
            201: TokenObtainPairResponseSerializer,
            400: "Bad request",
        },
    )
    def post(self, request: Request) -> Response:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            refresh = RefreshToken.for_user(serializer.instance)
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)


class UserExistsView(APIView):
    """Query if given username or email already exists"""

    authentication_classes = ()
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        tags=("auth",),
        security=[],
        operation_id="accounts_user_exists_read",
        operation_summary="Check if username or email is already in use",
        manual_parameters=(
            openapi.Parameter(
                "username",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "email",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
            ),
        ),
        responses={
            204: "Username or email already exist",
            400: "Bad request",
            status.HTTP_404_NOT_FOUND: "Username or email does not exist",
        },
    )
    def get(self, request: Request) -> Response:
        username = request.query_params.get("username")
        email = request.query_params.get("email")

        if username:
            UsernameValidator()(username)
            exists = UserModel.objects.filter(username=username).exists()
        elif email:
            EmailValidator()(email)
            exists = UserModel.objects.filter(email=email).exists()
        else:
            raise ParseError("Provide either username or email")

        if exists:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    """User Profile"""

    @swagger_auto_schema(
        tags=("users",),
        operation_id="accounts_user_profile_read",
        operation_summary="Get authenticated user's profile",
        responses={
            200: UserSerializer,
            401: "Unauthorized",
        },
    )
    def get(self, request: Request) -> Response:
        """Get user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=("users",),
        operation_summary="Update authenticated user's profile",
        request_body=UserSerializer,
        responses={
            200: UserSerializer,
            400: "Bad request",
            401: "Unauthorized",
        },
    )
    def patch(self, request: Request) -> Response:
        """Update user profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=("users",),
        operation_summary="Deactivate authenticated user's profile",
        responses={
            204: "Accout deactivated successfully",
            401: "Unauthorized",
        },
    )
    def delete(self, request: Request) -> Response:
        # Just deactivate the user
        # send_mail(
        #     subject="Flaam | Account deactivated",
        #     message="Your flaam account has been deactivated",
        #     from_email=None,
        #     recipient_list=[request.user.email],
        # )
        # TODO: add a delay period for deletion request
        request.user.is_active = False
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicUserProfileView(APIView):
    """Public User Profile"""

    @swagger_auto_schema(
        tags=("users",),
        operation_id="accounts_user_public_profile_read",
        operation_summary="Get public user's profile",
        responses={
            200: PublicUserSerializer,
            401: "Unauthorized",
            status.HTTP_404_NOT_FOUND: "Not found.",
        },
    )
    def get(self, request: Request, pk: int) -> Response:
        """Read public user profile"""
        user = get_object_or_404(UserModel, pk=pk)
        serializer = PublicUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
