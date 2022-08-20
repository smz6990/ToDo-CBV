from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from accounts.forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
# Create your views here.
class SignupCreateView(CreateView):
    """
    This is a class that handles sign up
    """
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("todo:index")
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        valid = super(SignupCreateView, self).form_valid(form)
        email = self.request.POST['email']
        password = self.request.POST['password1']
        user = authenticate(self.request, email=email, password=password)
        login(self.request, user)
        return valid