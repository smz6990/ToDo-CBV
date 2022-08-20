from django.contrib.auth.forms import UserCreationForm
from accounts.models import User

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']