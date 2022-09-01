import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from accounts.models import User


@pytest.fixture
def api_client():
    return APIClient


@pytest.mark.django_db
class TestAccountsApi:

    endpoint = "accounts:api-v1"

    def create_user_obj(self, is_verified=True):
        return User.objects.create_user(
            email="test@test.com",
            password="a/1234567",
            is_verified=is_verified,
        )

    def test_registration_post_201(self, api_client):
        client = api_client()
        registration_endpoint = reverse(f"{self.endpoint}:registration")
        data = {
            "email": "test@test.com",
            "password": "a/1234567",
            "password1": "a/1234567",
        }
        response = client.post(path=registration_endpoint, data=data)
        assert response.status_code == 201

    def test_registration_post_400_existing_email(self, api_client):
        # with existing email
        client = api_client()
        user = self.create_user_obj()
        registration_endpoint = reverse(f"{self.endpoint}:registration")
        data = {
            "email": "test@test.com",
            "password": "a/1234567",
            "password1": "a/1234567",
        }
        response = client.post(path=registration_endpoint, data=data)
        assert response.status_code == 400

    def test_registration_post_400_mismatch_password(self, api_client):
        # mismatch password
        client = api_client()
        registration_endpoint = reverse(f"{self.endpoint}:registration")
        data = {
            "email": "test@test.com",
            "password": "a/1234567",
            "password1": "a/7654321",
        }
        response = client.post(path=registration_endpoint, data=data)
        assert response.status_code == 400

    def test_token_login_post_200(self, api_client):
        client = api_client()
        login_endpoint = reverse(f"{self.endpoint}:token-login")
        user = self.create_user_obj()
        data = {"email": user.email, "password": "a/1234567"}
        response = client.post(path=login_endpoint, data=data)
        assert response.status_code == 200

    def test_token_login_post_403_logged_user(self, api_client):
        client = api_client()
        login_endpoint = reverse(f"{self.endpoint}:token-login")
        user = self.create_user_obj()
        client.force_authenticate(user)
        data = {"email": user.email, "password": "a/1234567"}
        response = client.post(path=login_endpoint, data=data)
        assert response.status_code == 403

    def test_token_logout_post_204(self, api_client):
        client = api_client()
        logout_endpoint = reverse(f"{self.endpoint}:token-logout")
        user = self.create_user_obj()
        client.force_authenticate(user)
        response = client.post(path=logout_endpoint, data=None)
        assert response.status_code == 204

    def test_token_logout_post_not_logged_user(self, api_client):
        client = api_client()
        logout_endpoint = reverse(f"{self.endpoint}:token-logout")
        response = client.post(path=logout_endpoint, data=None)
        assert response.status_code == 401

    def test_change_password_204(self, api_client):
        client = api_client()
        change_password_endpoint = reverse(
            f"{self.endpoint}:change-password"
        )
        user = self.create_user_obj()
        client.force_authenticate(user)
        data = {
            "old_password": "a/1234567",
            "new_password": "a/7654321",
            "new_password1": "a/7654321",
        }
        response = client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 204

    def test_change_password_400_wrong_password(self, api_client):
        # wrong old password
        client = api_client()
        change_password_endpoint = reverse(
            f"{self.endpoint}:change-password"
        )
        user = self.create_user_obj()
        client.force_authenticate(user)
        data = {
            "old_password": "a/7654321",
            "new_password": "a/7654321",
            "new_password1": "a/7654321",
        }
        response = client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 400

    def test_change_password_400_mismatch_password(self, api_client):
        # mismatch new password
        client = api_client()
        change_password_endpoint = reverse(
            f"{self.endpoint}:change-password"
        )
        user = self.create_user_obj()
        client.force_authenticate(user)
        data = {
            "old_password": "a/1234567",
            "new_password": "a/765765",
            "new_password1": "a/7654321",
        }
        response = client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 400

    def test_change_password_401_unauthorized_user(self, api_client):
        # Unauthorized  user
        client = api_client()
        change_password_endpoint = reverse(
            f"{self.endpoint}:change-password"
        )
        user = self.create_user_obj()
        data = {
            "old_password": "a/1234567",
            "new_password": "a/7654321",
            "new_password1": "a/7654321",
        }
        response = client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 401

    def test_send_verification_email_200(self, api_client):
        client = api_client()
        user = self.create_user_obj(is_verified=False)
        token = AccessToken.for_user(user)
        client.force_authenticate(user)
        send_email_endpoint = (
            f"/accounts/api/v1/verification/confirm/{token}/"
        )
        response = client.get(path=send_email_endpoint)
        assert response.status_code == 200

    def test_send_verification_email_400_invalid_token(self, api_client):
        client = api_client()
        user = self.create_user_obj(is_verified=False)
        token = AccessToken.for_user(user)
        client.force_authenticate(user)
        token = f"{str(token)}123"
        send_email_endpoint = (
            f"/accounts/api/v1/verification/confirm/{token}/"
        )
        response = client.get(path=send_email_endpoint)
        assert response.status_code == 400

    def test_resend_email_verification_200(self, api_client):
        client = api_client()
        resend_email_endpoint = reverse(f"{self.endpoint}:email-resend")
        user = self.create_user_obj(is_verified=False)
        data = {"email": user.email}
        response = client.post(path=resend_email_endpoint, data=data)
        assert response.status_code == 200

    def test_resend_email_verification_400_verified_user(self, api_client):
        # verified user
        client = api_client()
        resend_email_endpoint = reverse(f"{self.endpoint}:email-resend")
        user = self.create_user_obj(is_verified=True)
        data = {"email": user.email}
        response = client.post(path=resend_email_endpoint, data=data)
        assert response.status_code == 400

    def test_resend_email_verification_400_no_user(self, api_client):
        # test with no user with this email (dont exist)
        client = api_client()
        resend_email_endpoint = reverse(f"{self.endpoint}:email-resend")
        data = {"email": "test@test.com"}
        response = client.post(path=resend_email_endpoint, data=data)
        assert response.status_code == 400

    def test_password_reset_send_email_200(self, api_client):
        client = api_client()
        password_reset_endpoint = reverse(f"{self.endpoint}:password-reset")
        user = self.create_user_obj(is_verified=True)
        data = {"email": user.email}
        response = client.post(path=password_reset_endpoint, data=data)
        assert response.status_code == 200

    def test_password_reset_send_email_401_not_verified_user(
        self, api_client
    ):
        # user is not verified
        client = api_client()
        password_reset_endpoint = reverse(f"{self.endpoint}:password-reset")
        user = self.create_user_obj(is_verified=False)
        data = {"email": user.email}
        response = client.post(path=password_reset_endpoint, data=data)
        assert response.status_code == 401

    def test_password_reset_send_email_400_no_user(self, api_client):
        # user is not exist
        client = api_client()
        password_reset_endpoint = reverse(f"{self.endpoint}:password-reset")
        data = {"email": "test@test.com"}
        response = client.post(path=password_reset_endpoint, data=data)
        assert response.status_code == 400

    def test_done_password_reset_200(self, api_client):
        client = api_client()
        user = self.create_user_obj(is_verified=False)
        token = AccessToken.for_user(user)
        password_reset_done_endpoint = (
            f"/accounts/api/v1/password-reset/done/{token}/"
        )
        data = {"new_password": "a/9876543", "new_password1": "a/9876543"}
        response = client.put(path=password_reset_done_endpoint, data=data)
        assert response.status_code == 200

    def test_done_password_reset_400_mismatch_password(self, api_client):
        # mismatch password
        client = api_client()
        user = self.create_user_obj(is_verified=False)
        token = AccessToken.for_user(user)
        password_reset_done_endpoint = (
            f"/accounts/api/v1/password-reset/done/{token}/"
        )
        data = {"new_password": "a/9876543", "new_password1": "a/1234567"}
        response = client.put(path=password_reset_done_endpoint, data=data)
        assert response.status_code == 400

    def test_jwt_token_create_200(self, api_client):
        client = api_client()
        jwt_endpoint = reverse(f"{self.endpoint}:token-obtain-pair")
        user = self.create_user_obj()
        # client.force_authenticate(user=user)
        data = {"email": user.email, "password": "a/1234567"}
        response = client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 200

    def test_jwt_token_create_400_not_verified_user(self, api_client):
        # user not verified
        client = api_client()
        jwt_endpoint = reverse(f"{self.endpoint}:token-obtain-pair")
        user = self.create_user_obj(is_verified=False)
        # client.force_authenticate(user=user)
        data = {"email": user.email, "password": "a/1234567"}
        response = client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 400

    def test_jwt_token_create_401_not_existing_user(self, api_client):
        # user not exist
        client = api_client()
        jwt_endpoint = reverse(f"{self.endpoint}:token-obtain-pair")
        data = {"email": "test@test.com", "password": "a/1234567"}
        response = client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 401

    def test_jwt_token_refresh_200(self, api_client):
        client = api_client()
        jwt_endpoint = reverse(f"{self.endpoint}:token-refresh")
        user = self.create_user_obj()
        # client.force_authenticate(user=user)
        refresh = str(RefreshToken.for_user(user))
        data = {"refresh": refresh}
        response = client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 200

    def test_jwt_token_refresh_401_invalid_token(self, api_client):
        # corrupted token
        client = api_client()
        jwt_endpoint = reverse(f"{self.endpoint}:token-refresh")
        user = self.create_user_obj()
        # client.force_authenticate(user=user)
        refresh = f"{str(RefreshToken.for_user(user))}123"
        data = {"refresh": refresh}
        response = client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 401
