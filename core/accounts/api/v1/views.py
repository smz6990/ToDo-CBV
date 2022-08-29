from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegistrationSerializer, CustomAuthTokenSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer,
    )
from .permissions import NotAuthenticated


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
        data = {'email': serializer.validated_data['email']}
        return Response(data, status=status.HTTP_201_CREATED)
    
class CustomAuthTokenView(ObtainAuthToken):
    """
    Custom Login with Token Authentication
    """
    serializer_class = CustomAuthTokenSerializer
    permission_classes = [NotAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
        
class CustomDiscardTokenView(APIView):
    """
    Deleting token of user
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.user.auth_token.delete()
        data = {"detail":"Token deleted successfully"}
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
            return Response({"detail": "User is not verified"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong password."]},status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CustomTokenObtainPairView(TokenObtainPairView):
      
    serializer_class = CustomTokenObtainPairSerializer
    