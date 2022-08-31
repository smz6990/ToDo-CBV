from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Model serializer to register (sign up) a new user
    """

    password1 = serializers.CharField(max_length=128, required=True)

    class Meta:
        model = User
        fields = ["email", "password", "password1"]

    def validate(self, attrs):
        """
        Validating password
        """
        if attrs.get("password") != attrs.get("password1"):
            raise serializers.ValidationError(
                {"details": "Passwords did not match"}
            )
        try:
            validate_password(attrs.get("password"))
        except ValidationError as e:
            raise serializers.ValidationError(
                {"Password": list(e.messages)}
            ) from e
        return super().validate(attrs)

    def create(self, validated_data):
        """
        Creating a new user
        """
        validated_data.pop("password1", None)
        return User.objects.create_user(**validated_data)


class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for CustomAuthTokenView for login with email and token
    """

    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                username=email,
                password=password,
            )
            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
            if not user.is_verified:
                msg = _("User is not verified.")
                raise serializers.ValidationError(msg, code="Verification")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for change password
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError(
                {"detail": "passwords did not match"}
            )
        try:
            validate_password(attrs.get("new_password"))
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        return super().validate(attrs)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError(
                {"detail": "User is not verified"}
            )
        validated_data["email"] = self.user.email
        validated_data["user_id"] = self.user.id
        return validated_data


class EmailResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            raise serializers.ValidationError(
                {"detail": "User Does not exist"}
            ) from e
        if user.is_verified:
            raise serializers.ValidationError(
                {"detail": "User is already verified"}
            )
        attrs["user"] = user
        return super().validate(attrs)


class PasswordResetSendSerializer(serializers.Serializer):
    """
    serializer for reset the password to send reset email
    """

    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            raise serializers.ValidationError(
                {"detail": "User Does not exist"}
            ) from e
        attrs["user"] = user
        return super().validate(attrs)


class PasswordResetDoneSerializer(serializers.Serializer):
    """
    serializer for reset the password after getting token
    """

    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError(
                {"detail": "passwords did not match"}
            )
        try:
            validate_password(attrs.get("new_password"))
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        return super().validate(attrs)
