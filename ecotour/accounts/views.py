from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, LoginForm
from django.contrib.auth.models import User
from .models import RefreshTokenModel
from rest_framework_simplejwt.tokens import RefreshToken


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
            # username = form.cleaned_data.get("username")
            # raw_password = form.cleaned_data.get("password1")
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            # return redirect("/")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Issue JWT token
                token_instance = RefreshTokenModel.create_token(user)

                # Render the login_success.html template
                response = render(
                    request,
                    "accounts/login_success.html",
                    {
                        "refresh": token_instance.token,
                        "access": str(RefreshToken(token_instance.token).access_token),
                    },
                )
                response["Content-Security-Policy"] = (
                    "script-src 'self' 'unsafe-inline'"
                )
                return response
                # return redirect("/")
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    RefreshTokenModel.objects.filter(user=request.user).delete()
    logout(request)
    return render(request, "accounts/logout.html")
    # return redirect("/")
