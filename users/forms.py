from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User


class UserRegisterForm(auth_forms.UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]
        required = ["username"]


class LoginForm(auth_forms.AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]
