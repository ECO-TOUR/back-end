from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LoginForm
from .models import RefreshTokenModel
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from django.conf import settings


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

                refresh = token_instance.token
                access_token = (str(RefreshToken(token_instance.token).access_token),)

                # Create response to redirect to the main page
                response = redirect(reverse("index"))

                # Set the JWT token in the cookies
                secure_cookie = settings.ENVIRONMENT == "production"
                response.set_cookie(
                    "access",
                    access_token,
                    httponly=True,
                    secure=secure_cookie,
                    samesite="Lax",
                )
                response.set_cookie(
                    "refresh",
                    str(refresh),
                    httponly=True,
                    secure=secure_cookie,
                    samesite="Lax",
                )
                return response
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    # RefreshTokenModel.objects.filter(user=request.user).delete()
    refresh_token = request.COOKIES.get("refresh")
    if refresh_token:
        try:
            token_instance = RefreshTokenModel.objects.get(token=refresh_token)
            token_instance.blacklist()
        except RefreshTokenModel.DoesNotExist:
            pass

    logout(request)
    response = redirect("/")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response
