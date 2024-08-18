from datetime import timedelta
from pathlib import Path

import environ
import jwt
import requests
from common.decorators import jwt_required
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import LoginForm, SignUpForm
from .models import CustomUser, RefreshTokenModel
from .serializers import CustomUserSerializer, KaKaoLoginSerializer, LoginSerializer

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# read env config
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env_path = BASE_DIR.parent / ".env"
environ.Env.read_env(env_file=env_path)

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
            nickname = form.cleaned_data.get("nickname")
            password = form.cleaned_data.get("password")
            profile_photo = form.cleaned_data.get("profile_photo")
            user = authenticate(request, username=username, password=password)
            if user is None:
                # If user does not exist, create a new one
                user = User.objects.create_user(username=username, password=password, nickname=nickname, profile_photo=profile_photo)
                user.save()
                # Automatically log in the new user
                user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # Issue JWT token
                token_instance = RefreshTokenModel.create_token(user)

                refresh_token = token_instance.token
                access_token = str(RefreshToken(token_instance.token).access_token)

                # Create response to redirect to the main page
                response = redirect(reverse("index"))

                # Set the JWT token in the cookies
                secure_cookie = settings.ENVIRONMENT == "production"
                response.set_cookie("access_token", access_token, httponly=True, secure=secure_cookie, samesite="Lax")
                response.set_cookie("refresh_token", str(refresh_token), httponly=True, secure=secure_cookie, samesite="Lax")
                return response
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token:
        try:
            token_instance = RefreshTokenModel.objects.get(token=refresh_token)
            token_instance.blacklist()
        except RefreshTokenModel.DoesNotExist:
            pass

    oauth_kakao_logout_view(request)
    logout(request)

    response = redirect("/")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
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

            refresh_token = token_instance.token
            access_token = str(RefreshToken(token_instance.token).access_token)

            return Response({"refresh_token": str(refresh_token), "access_token": access_token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(jwt_required, name="dispatch")
class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token_instance = RefreshTokenModel.objects.get(token=refresh_token)
                token_instance.blacklist()
            except RefreshTokenModel.DoesNotExist:
                pass

        logout(request)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


def authorize_code_kakao(request):
    scope = request.GET.get("scope", "")
    scope_param = f"&scope={scope}" if scope else ""
    client_id = env("KAKAO_CLIENT_ID")
    redirect_uri = env("KAKAO_REDIRECT_URI")
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code{scope_param}")


def call(method, uri, data, header, query_params=None):
    if query_params:
        response = requests.request(method, uri, headers=header, data=data, params=query_params)
    else:
        response = requests.request(method, uri, headers=header, data=data)
    return response.json()


def oauth_kakao_login_view(request):
    code = request.GET.get("code")
    data = {"grant_type": "authorization_code", "client_id": env("KAKAO_CLIENT_ID"), "redirect_uri": env("KAKAO_REDIRECT_URI"), "code": code}
    header = {"content-type": "application/x-www-form-urlencoded"}
    token_uri = "https://kauth.kakao.com/oauth/token"
    response_token = call("POST", token_uri, data, header)
    request.session["access_token_kakao"] = response_token["access_token"]
    request.session["refresh_token_kakao"] = response_token["refresh_token"]

    response_oicd = call("GET", "https://kapi.kakao.com/v1/oidc/userinfo", {}, {"Authorization": f'Bearer {response_token["access_token"]}'})
    request.session["user_id"] = int(response_oicd["sub"])

    # Authenticate user
    user = authenticate(request, username=response_oicd["nickname"], password="dummy")

    if user is None:
        # If user does not exist, create a new one
        user = User.objects.create_user(
            username=response_oicd["nickname"],
            password="dummy",  # No password needed for OAuth login
            nickname=response_oicd["nickname"],
            profile_photo=response_oicd["picture"],
        )
        # Log the user in
    login(request, user)
    # Issue JWT token
    token_instance = RefreshTokenModel.create_token(user)

    refresh_token = token_instance.token
    access_token = str(RefreshToken(token_instance.token).access_token)

    # Create response to redirect to the main page
    response = redirect(reverse("index"))

    # Set the JWT token in the cookies
    secure_cookie = settings.ENVIRONMENT == "production"
    response.set_cookie("access_token", access_token, httponly=True, secure=secure_cookie, samesite="Lax")
    response.set_cookie("refresh_token", str(refresh_token), httponly=True, secure=secure_cookie, samesite="Lax")
    return response


def oauth_kakao_logout_view(request):
    if request.session.get("user_id"):

        uri = "https://kapi.kakao.com/v1/user/logout"
        header = {"Authorization": f"Bearer {request.session.get('access_token_kakao')}"}

        data = {"target_id_type": "user_id", "target_id": request.session.get("user_id")}

        response_logout = call("POST", uri, data, header)

        return JsonResponse(response_logout)


class OauthKaKaoLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Initialize the serializer with incoming request data
        serializer = KaKaoLoginSerializer(data=request.data)

        # Validate the data (Deserialization)
        if serializer.is_valid():
            # Access the validated data
            code = serializer.validated_data["code"]

            if not code:
                return JsonResponse({"error": "Code is required"}, status=400)

            # Exchange the code for tokens
            data = {
                "grant_type": "authorization_code",
                "client_id": env("KAKAO_CLIENT_ID"),
                "redirect_uri": env("KAKAO_REDIRECT_URI_FRONT"),
                "code": code,
            }
            header = {"Content-Type": "application/x-www-form-urlencoded"}
            token_uri = "https://kauth.kakao.com/oauth/token"
            response_token = call("POST", token_uri, data, header)
            # Handle error response from token request
            if "error" in response_token:
                return Response(response_token, status=status.HTTP_400_BAD_REQUEST)

            kakao_access_token = response_token["access_token"]
            kakao_refresh_token = response_token["refresh_token"]
            kakao_id_token = response_token.get("id_token")
            kakao_expires_in = response_token["refresh_token_expires_in"]
            kakao_expires_at = timezone.now() + timedelta(seconds=kakao_expires_in)

            # Fetch user info from Kakao
            response_oicd = call("GET", "https://kapi.kakao.com/v1/oidc/userinfo", {}, {"Authorization": f"Bearer {kakao_access_token}"})

            # Authenticate the user
            user = authenticate(request, username=response_oicd["nickname"], password="dummy")

            if user is None:
                # If the user does not exist, create a new one
                user = User.objects.create_user(
                    username=response_oicd["nickname"],
                    password="dummy",  # No password needed for OAuth login
                    nickname=response_oicd["nickname"],
                    profile_photo=response_oicd["picture"],
                )

            user.oauth_kakao_access_token = kakao_access_token
            user.oauth_kakao_refresh_token = kakao_refresh_token
            user.oauth_kakao_id_token = kakao_id_token
            user.oauth_kakao_expires_at = kakao_expires_at
            user.save()

            # Log the user in
            login(request, user)

            # Issue JWT token
            token_instance = RefreshTokenModel.create_token(user)
            refresh_token = token_instance.token
            access_token_jwt = str(RefreshToken(token_instance.token).access_token)

            # Create the response data (Serialization)
            response_data = {
                "statusCode": 200,
                "message": "OK",
                "content": {
                    "user": {
                        "user_id": user.user_id,
                        "username": user.username,
                        "nickname": user.nickname,
                        "profile_photo": (user.profile_photo if user.profile_photo else None),
                    },
                    "refresh_token": str(refresh_token),
                    "access_token": access_token_jwt,
                },
            }

            # Return the response
            return Response(response_data, status=status.HTTP_200_OK)

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(jwt_required, name="dispatch")
class OauthKaKaoLogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the user ID from the request (set by the jwt_required decorator)
        access_token = request.COOKIES.get("access_token")

        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("user_id")

        # Retrieve the user from the database
        try:
            user = CustomUser.objects.get(user_id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Use the stored access_token to get user info from Kakao
        user_info_uri = "https://kapi.kakao.com/v1/user/access_token_info"
        headers = {"Authorization": f"Bearer {user.oauth_kakao_access_token}"}

        response_user_info = call("GET", user_info_uri, {}, headers)

        if "error" in response_user_info:
            return Response(response_user_info, status=status.HTTP_400_BAD_REQUEST)

        # Get the Kakao user ID from the response
        kakao_user_id = response_user_info.get("id")

        # Logout the user from Kakao
        logout_uri = "https://kapi.kakao.com/v1/user/logout"
        headers = {"Authorization": f"Bearer {user.oauth_kakao_access_token}"}
        data = {"target_id_type": "user_id", "target_id": kakao_user_id}
        response_logout = call("POST", logout_uri, data, headers)

        if "error" in response_logout:
            return Response(response_logout, status=status.HTTP_400_BAD_REQUEST)

        # Invalidate the user's OAuth tokens in your database
        user.oauth_kakao_access_token = None
        user.oauth_kakao_refresh_token = None
        user.oauth_kakao_id_token = None
        user.oauth_kakao_expires_at = None
        user.save()

        # Log the user out from the Django session
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token_instance = RefreshTokenModel.objects.get(token=refresh_token)
                token_instance.blacklist()
            except RefreshTokenModel.DoesNotExist:
                pass
        logout(request)

        # Clear cookies

        response = Response({"statusCode": 200, "message": "OK", "content": {"detail": "Logged out successfully"}}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


@method_decorator(jwt_required, name="dispatch")
class OauthKaKaoSignoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the user ID from the request (set by the jwt_required decorator)
        access_token = request.COOKIES.get("access_token")

        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("user_id")

        # Retrieve the user from the database
        try:
            user = CustomUser.objects.get(user_id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Use the stored access_token to get user info from Kakao
        user_info_uri = "https://kapi.kakao.com/v1/user/access_token_info"
        headers = {"Authorization": f"Bearer {user.oauth_kakao_access_token}"}

        response_user_info = call("GET", user_info_uri, {}, headers)

        if "error" in response_user_info:
            return Response(response_user_info, status=status.HTTP_400_BAD_REQUEST)

        # Get the Kakao user ID from the response
        kakao_user_id = response_user_info.get("id")

        # Logout the user from Kakao
        logout_uri = "https://kapi.kakao.com/v1/user/logout"
        headers = {"Authorization": f"Bearer {user.oauth_kakao_access_token}"}
        data = {"target_id_type": "user_id", "target_id": kakao_user_id}
        response_logout = call("POST", logout_uri, data, headers)

        if "error" in response_logout:
            return Response(response_logout, status=status.HTTP_400_BAD_REQUEST)

        response_delete = user.delete()

        if response_delete:
            response = Response({"statusCode": 200, "message": "OK", "content": {"detail": "Signout successfully"}}, status=status.HTTP_200_OK)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            return response

        return Response({"delete error"}, status=status.HTTP_400_BAD_REQUEST)


def profile(request):
    uri = "https://kapi.kakao.com/v2/user/me"
    header = {"Authorization": f"Bearer {request.session.get('access_token_kakao')}"}
    rtn = call("POST", uri, {}, header)
    return JsonResponse(rtn)
