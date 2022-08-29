from django.urls import path
from rest_framework_simplejwt.views import(
    TokenRefreshView,
    TokenVerifyView
)
from . import views


app_name = 'api-v1'

urlpatterns = [
    path('registration/', views.RegistrationCreateApiView.as_view(), name='registration'),
    path('token/login/', views.CustomAuthTokenView.as_view(), name='token-login'),
    path('token/logout/', views.CustomDiscardTokenView.as_view(), name='token-login'),
    path('registration/change-password/', views.ChangePasswordAPIView.as_view(), name='change-password'),
    
    path('jwt/create/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
]
