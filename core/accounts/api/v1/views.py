from urllib import response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated

from .serializers import RegistrationSerializer, CustomAuthTokenSerializer
from .permissions import NotAuthenticated

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