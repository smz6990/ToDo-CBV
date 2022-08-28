from django.urls import path
from . import views

app_name = 'api-v1'

urlpatterns = [
    path('registration/', views.RegistrationCreateApiView.as_view(), name='registration'),
    path('token/login/', views.CustomAuthTokenView.as_view(), name='token-login'),
    path('token/logout/', views.CustomDiscardTokenView.as_view(), name='token-login'),
    
]
