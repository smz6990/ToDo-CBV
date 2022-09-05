import pytest
from django.urls import reverse
from rest_framework .test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from accounts.models import User


@pytest.fixture
def api_client():
    client = APIClient()
    return  client

@pytest.fixture
def create_user_obj():
    user = User.objects.create_user(email='test@test.com', password='a/1234567', is_verified=True)
    return user

@pytest.fixture
def not_verified_user(create_user_obj):
    user = create_user_obj
    user.is_verified = False
    user.save()
    return user

@pytest.mark.django_db
class TestAccountsApi:
    
    endpoint = 'accounts:api-v1'
    
    def test_registration_post_201(self, api_client):
        registration_endpoint = reverse( f'{self.endpoint}:registration' )
        data = {'email':'test@test.com', 'password':'a/1234567', 'password1':'a/1234567'}
        response = api_client.post(path=registration_endpoint, data=data)
        assert response.status_code == 201
    
    def test_registration_post_400_existing_email(self, api_client, create_user_obj):
        # with existing email
        user = create_user_obj
        registration_endpoint = reverse( f'{self.endpoint}:registration' )
        data = {'email':'test@test.com', 'password':'a/1234567', 'password1':'a/1234567'}
        response = api_client.post(path=registration_endpoint, data=data)
        assert response.status_code == 400
    
    def test_registration_post_400_mismatch_password(self, api_client):
        # mismatch password
        registration_endpoint = reverse( f'{self.endpoint}:registration' )
        data = {'email':'test@test.com', 'password':'a/1234567', 'password1':'a/7654321'}
        response = api_client.post(path=registration_endpoint, data=data)
        assert response.status_code == 400
        
    def test_token_login_post_200(self, api_client, create_user_obj):
        login_endpoint = reverse( f'{self.endpoint}:token-login' )
        user = create_user_obj
        data = {'email':user.email, 'password':'a/1234567'}
        response = api_client.post(path=login_endpoint, data=data)
        assert response.status_code == 200

    def test_token_login_post_403_logged_user(self, api_client, create_user_obj):
        login_endpoint = reverse( f'{self.endpoint}:token-login' )
        user = create_user_obj
        api_client.force_authenticate(user)
        data = {'email':user.email, 'password':'a/1234567'}
        response = api_client.post(path=login_endpoint, data=data)
        assert response.status_code == 403
       
    def test_token_logout_post_204(self, api_client, create_user_obj):
        logout_endpoint = reverse( f'{self.endpoint}:token-logout' )
        user = create_user_obj
        api_client.force_authenticate(user)
        response = api_client.post(path=logout_endpoint, data=None)
        assert response.status_code == 204
    
    def test_token_logout_post_not_logged_user(self, api_client):
        logout_endpoint = reverse( f'{self.endpoint}:token-logout' )
        response = api_client.post(path=logout_endpoint, data=None)
        assert response.status_code == 401
    
    def test_change_password_204(self, api_client, create_user_obj):
        change_password_endpoint = reverse( f'{self.endpoint}:change-password' )
        user = create_user_obj
        api_client.force_authenticate(user)
        data = {'old_password':'a/1234567', 'new_password':'a/7654321', 'new_password1':'a/7654321'}
        response = api_client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 204
    
    def test_change_password_400_wrong_password(self, api_client, create_user_obj):
        # wrong old password
        change_password_endpoint = reverse( f'{self.endpoint}:change-password' )
        user = create_user_obj
        api_client.force_authenticate(user)
        data = {'old_password':'a/7654321', 'new_password':'a/7654321', 'new_password1':'a/7654321'}
        response = api_client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 400
    
    def test_change_password_400_mismatch_password(self, api_client, create_user_obj):
        # mismatch new password
        change_password_endpoint = reverse( f'{self.endpoint}:change-password' )
        user = create_user_obj
        api_client.force_authenticate(user)
        data = {'old_password':'a/1234567', 'new_password':'a/765765', 'new_password1':'a/7654321'}
        response = api_client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 400
    
    def test_change_password_401_unauthorized_user(self, api_client, create_user_obj):
        # Unauthorized  user
        change_password_endpoint = reverse( f'{self.endpoint}:change-password' )
        user = create_user_obj
        data = {'old_password':'a/1234567', 'new_password':'a/7654321', 'new_password1':'a/7654321'}
        response = api_client.put(path=change_password_endpoint, data=data)
        assert response.status_code == 401
    
    def test_send_verification_email_200(self, api_client, not_verified_user):
        user = not_verified_user
        token = AccessToken.for_user(user)
        api_client.force_authenticate(user)
        send_email_endpoint =  f'/accounts/api/v1/verification/confirm/{token}/'
        response = api_client.get(path=send_email_endpoint)
        assert response.status_code == 200
    
    def test_send_verification_email_400_invalid_token(self, api_client, not_verified_user):
        user = not_verified_user
        token = AccessToken.for_user(user)
        api_client.force_authenticate(user)
        token = f'{str(token)}123'
        send_email_endpoint = f'/accounts/api/v1/verification/confirm/{token}/'
        response = api_client.get(path=send_email_endpoint)
        assert response.status_code == 400
       
    def test_resend_email_verification_200(self, api_client, not_verified_user):
        resend_email_endpoint = reverse( f'{self.endpoint}:email-resend' )
        user = not_verified_user
        data = {'email':user.email}
        response = api_client.post(path=resend_email_endpoint, data=data)
        assert response.status_code == 200 
    
    def test_resend_email_verification_400_verified_user(self, api_client, create_user_obj):
        # verified user
        resend_email_endpoint = reverse( f'{self.endpoint}:email-resend' )
        user = create_user_obj
        data = {'email':user.email}
        response = api_client.post(path=resend_email_endpoint, data=data)
        assert response.status_code == 400
        
    def test_resend_email_verification_400_no_user(self, api_client):
        # test with no user with this email (dont exist)
        resend_email_endpoint = reverse( f'{self.endpoint}:email-resend' )
        data = {'email':'test@test.com'}
        response = api_client.post(path=resend_email_endpoint, data=data)
        assert response.status_code == 400
    
    def test_password_reset_send_email_200(self, api_client, create_user_obj):
        password_reset_endpoint = reverse( f'{self.endpoint}:password-reset' )
        user = create_user_obj
        data = {'email':user.email}
        response = api_client.post(path=password_reset_endpoint, data=data)
        assert response.status_code == 200 
    
    def test_password_reset_send_email_401_not_verified_user(self, api_client, not_verified_user):
        # user is not verified
        password_reset_endpoint = reverse( f'{self.endpoint}:password-reset' )
        user = not_verified_user
        data = {'email':user.email}
        response = api_client.post(path=password_reset_endpoint, data=data)
        assert response.status_code == 401
    
    def test_password_reset_send_email_400_no_user(self, api_client):
        # user is not exist
        password_reset_endpoint = reverse( f'{self.endpoint}:password-reset' )
        data = {'email':'test@test.com'}
        response = api_client.post(path=password_reset_endpoint, data=data)
        assert response.status_code == 400
    
    def test_done_password_reset_200(self, api_client, not_verified_user):
        user = not_verified_user
        token = AccessToken.for_user(user)
        password_reset_done_endpoint = f'/accounts/api/v1/password-reset/done/{token}/'
        data = {'new_password':'a/9876543', 'new_password1':'a/9876543'}
        response = api_client.put(path=password_reset_done_endpoint, data=data)
        assert response.status_code == 200
    
    def test_done_password_reset_400_mismatch_password(self, api_client, not_verified_user):
        # mismatch password
        user = not_verified_user
        token = AccessToken.for_user(user)
        password_reset_done_endpoint = f'/accounts/api/v1/password-reset/done/{token}/'
        data = {'new_password':'a/9876543', 'new_password1':'a/1234567'}
        response = api_client.put(path=password_reset_done_endpoint, data=data)
        assert response.status_code == 400
    
    def test_jwt_token_create_200(self, api_client, create_user_obj): 
        jwt_endpoint = reverse( f'{self.endpoint}:token-obtain-pair' )
        user = create_user_obj
        data = {'email':user.email, 'password':'a/1234567'}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 200
    
    def test_jwt_token_create_400_not_verified_user(self, api_client, not_verified_user):
        # user not verified
        jwt_endpoint = reverse( f'{self.endpoint}:token-obtain-pair' )
        user = not_verified_user
        data = {'email':user.email, 'password':'a/1234567'}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 400
    
    def test_jwt_token_create_401_not_existing_user(self, api_client):
        # user not exist
        jwt_endpoint = reverse( f'{self.endpoint}:token-obtain-pair' )
        data = {'email':'test@test.com', 'password':'a/1234567'}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 401
    
    def test_jwt_token_refresh_200(self, api_client, create_user_obj):
        jwt_endpoint = reverse( f'{self.endpoint}:token-refresh' )
        user = create_user_obj
        refresh = str(RefreshToken.for_user(user))
        data = {"refresh":refresh}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 200
    
    def test_jwt_token_refresh_401_invalid_token(self, api_client, create_user_obj):
        # corrupted token
        jwt_endpoint = reverse( f'{self.endpoint}:token-refresh' )
        user = create_user_obj
        refresh = f'{str(RefreshToken.for_user(user))}123'
        data = {"refresh":refresh}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 401
        
    def test_jwt_token_verify_200_with_token_refresh(self, api_client, create_user_obj):
        jwt_endpoint = reverse(f"{self.endpoint}:token-verify")
        user = create_user_obj
        token = f"{str(RefreshToken.for_user(user))}"
        data = {"token": token}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 200

    def test_jwt_token_verify_200_with_token_access(self, api_client, create_user_obj):
        jwt_endpoint = reverse(f"{self.endpoint}:token-verify")
        user = create_user_obj
        token = f"{str(RefreshToken.for_user(user).access_token)}"
        data = {"token": token}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 200

    def test_jwt_token_verify_401_with_invalid_token(self, api_client, create_user_obj):
        jwt_endpoint = reverse(f"{self.endpoint}:token-verify")
        user = create_user_obj
        token = f"{str(RefreshToken.for_user(user))}123"
        data = {"token": token}
        response = api_client.post(path=jwt_endpoint, data=data)
        assert response.status_code == 401