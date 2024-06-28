from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, required=False)
    profile_photo = forms.CharField(max_length=255, required=False)  # Set profile_photo as not required
    nickname = forms.CharField(max_length=255, required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "profile_photo", "nickname", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields["email"].required = False
        self.fields["nickname"].required = True
        self.fields["password1"].required = False
        self.fields["password2"].required = False

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return email


class LoginForm(forms.Form):
    username = forms.CharField()
    profile_photo = forms.CharField(max_length=255, required=False)  # Set profile_photo as not required
    nickname = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("username", "nickname", "password")

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["nickname"].required = False
        self.fields["password"].required = False
