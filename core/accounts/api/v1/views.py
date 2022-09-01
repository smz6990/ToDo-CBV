from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from mail_templated import EmailMessage
from .serializers import (
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    EmailResendSerializer,
    PasswordResetSendSerializer,
    PasswordResetDoneSerializer,
)
from .permissions import NotAuthenticated
from accounts.utils import EmailThreading
from django.conf import settings
import jwt

User = get_user_model()


class RegistrationCreateApiView(CreateAPIView):
    """
    register a new user (signup)
    """

    permission_classes = [NotAuthenticated]
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        """
        rewrite the post method to register a new user
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data["email"]
        data = {"email": email}
        user = User.objects.get(email=email)
        token = self.get_token_for_user(user)
        message = EmailMessage(
            "email/verification_mail.tpl",
            {"token": token},
            "noreply@example.com",
            to=[email],
        )
        EmailThreading(message).start()
        return Response(data, status=status.HTTP_201_CREATED)

    def get_token_for_user(self, user):
        access = AccessToken.for_user(user)
        return str(access)


class CustomAuthTokenView(ObtainAuthToken):
    """
    Custom Login with Token Authentication
    """

    serializer_class = CustomAuthTokenSerializer
    permission_classes = [NotAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "email": user.email}
        )


class CustomDiscardTokenView(APIView):
    """
    Deleting token of user
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        data = {"detail": "Token deleted successfully"}
        return Response(data, status=status.HTTP_204_NO_CONTENT)


class ChangePasswordAPIView(GenericAPIView):
    """
    An endpoint for changing password.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_verified:
            return Response(
                {"detail": "User is not verified"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    getting refresh and access token with user_id and email
    """

    serializer_class = CustomTokenObtainPairSerializer


class EmailVerificationAPIView(APIView):
    """
    View to send email verification to user
    """

    def get(self, request, token, *args, **kwargs):
        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response(
                {"email": "your account successfully activated"},
                status=status.HTTP_200_OK,
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activations link expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST
            )


class EmailResendAPIView(GenericAPIView):
    """
    view to resend email for user verification
    """

    serializer_class = EmailResendSerializer
    permission_classes = [NotAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        token = AccessToken.for_user(user)
        message = EmailMessage(
            "email/verification_mail.tpl",
            {"token": token},
            "noreply@example.com",
            to=[user.email],
        )

        EmailThreading(message).start()
        return Response(
            {"Detail": "Email for activating your account sent successfully"},
            status=status.HTTP_200_OK,
        )


class PasswordResetSendAPIView(GenericAPIView):
    """
    class that send reset password email with token for user
    """

    serializer_class = PasswordResetSendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        if not user.is_verified:
            return Response(
                {"detail": "User is not verified"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token = AccessToken.for_user(user)
        message = EmailMessage(
            "email/reset_password.tpl",
            {"token": token},
            "noreply@example.com",
            to=[user.email],
        )

        EmailThreading(message).start()
        return Response(
            {"detail": "Email for reset password sent successfully"},
            status=status.HTTP_200_OK,
        )


class PasswordResetDoneAPIView(GenericAPIView):
    """
    changing password if token is valid
    """

    serializer_class = PasswordResetDoneSerializer
    model = User

    def put(self, request, token, *args, **kwargs):
        try:
            payload = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = User.objects.get(id=payload["user_id"])

        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activations link expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response(
            {"email": "your new password successfully changed"},
            status=status.HTTP_200_OK,
        )
