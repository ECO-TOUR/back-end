from common.decorators import jwt_required
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import LoginForm, SignUpForm
from .models import RefreshTokenModel
from .serializers import CustomUserSerializer, LoginSerializer

User = get_user_model()


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
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
                access_token = str(RefreshToken(token_instance.token).access_token)

                # Create response to redirect to the main page
                response = redirect(reverse("index"))

                # Set the JWT token in the cookies
                secure_cookie = settings.ENVIRONMENT == "production"
                response.set_cookie("access", access_token, httponly=True, secure=secure_cookie, samesite="Lax")
                response.set_cookie("refresh", str(refresh), httponly=True, secure=secure_cookie, samesite="Lax")
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


class SignUpAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            # Issue JWT token
            token_instance = RefreshTokenModel.create_token(user)

            refresh = token_instance.token
            access_token = str(RefreshToken(token_instance.token).access_token)

            return Response({"refresh": str(refresh), "access": access_token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(jwt_required, name="dispatch")
class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh")
        if refresh_token:
            try:
                token_instance = RefreshTokenModel.objects.get(token=refresh_token)
                token_instance.blacklist()
            except RefreshTokenModel.DoesNotExist:
                pass

        logout(request)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
