from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text="Required")
    profile_photo = forms.CharField(max_length=255, required=False)  # Set profile_photo as not required
    nickname = forms.CharField(max_length=255, required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "profile_photo", "nickname", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Email is required")
        return email


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
