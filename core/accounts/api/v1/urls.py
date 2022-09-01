from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views


app_name = "api-v1"

urlpatterns = [
    path(
        "registration/",
        views.RegistrationCreateApiView.as_view(),
        name="registration",
    ),
    path(
        "token/login/",
        views.CustomAuthTokenView.as_view(),
        name="token-login",
    ),
    path(
        "token/logout/",
        views.CustomDiscardTokenView.as_view(),
        name="token-logout",
    ),
    path(
        "registration/change-password/",
        views.ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    path(
        "verification/confirm/<str:token>/",
        views.EmailVerificationAPIView.as_view(),
        name="email-verification",
    ),
    path(
        "verification/resend/",
        views.EmailResendAPIView.as_view(),
        name="email-resend",
    ),
    # reset password and password confirm
    path(
        "password-reset/send/",
        views.PasswordResetSendAPIView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset/done/<str:token>/",
        views.PasswordResetDoneAPIView.as_view(),
        name="password-reset-done",
    ),
    path(
        "jwt/create/",
        views.CustomTokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token-verify"),
]
