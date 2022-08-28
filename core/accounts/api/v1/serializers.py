from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Model serializer to register (sign up) a new user
    """
    password1 = serializers.CharField(max_length=128,required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password1']
        
    def validate(self, attrs):
        """
        Validating password
        """
        if attrs.get('password') != attrs.get('password1'):
            raise serializers.ValidationError({'details': 'Passwords did not match'})
        try:
            validate_password(attrs.get('password'))
        except ValidationError as e:
            raise serializers.ValidationError({'Password': list(e.messages)}) from e
        return super().validate(attrs)
    
    def create(self, validated_data):
        """
        Creating a new user
        """
        validated_data.pop('password1', None)
        return User.objects.create_user(**validated_data)
    
    

class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for CustomAuthTokenView for login with email and token
    """
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
