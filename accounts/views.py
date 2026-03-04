"""
Views for user authentication and account management.
"""
import logging

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.permissions import IsManager
from core.responses import created_response, error_response, success_response

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserListSerializer,
    UserResponseSerializer,
)

User = get_user_model()
logger = logging.getLogger('apps')


class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Authenticate user and return JWT tokens with user info.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class RefreshTokenView(TokenRefreshView):
    """
    POST /api/v1/auth/token/refresh/
    Refresh an access token using a valid refresh token.
    """
    permission_classes = [AllowAny]


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Register a new user account.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info('New user registered: %s (role: %s)', user.username, user.role)

        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        return created_response(
            data={
                'user': UserResponseSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            },
            message='Registration successful.',
        )


class LogoutView(generics.GenericAPIView):
    """
    POST /api/v1/auth/logout/
    Blacklist the refresh token to log out.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return error_response(
                    message='Refresh token is required.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info('User logged out: %s', request.user.username)
            return success_response(message='Logged out successfully.')
        except Exception:
            return error_response(
                message='Invalid or expired token.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(generics.RetrieveAPIView):
    """
    GET /api/v1/auth/profile/
    Retrieve the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserResponseSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    """
    PUT /api/v1/auth/change-password/
    Change the authenticated user's password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info('Password changed for user: %s', request.user.username)
        return success_response(message='Password changed successfully.')


class UserListView(generics.ListAPIView):
    """
    GET /api/v1/auth/users/
    List all users (manager only).
    """
    permission_classes = [IsManager]
    serializer_class = UserListSerializer
    queryset = User.objects.all().order_by('-date_joined')
