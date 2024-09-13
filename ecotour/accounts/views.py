import json
from datetime import timedelta
from pathlib import Path

import environ
import jwt
import requests
import requests.cookies
from common.decorators import jwt_required
from community.models import KeywordRating, TourKeyword, User_Preference
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

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

                # 쿠키 방식 주석처리
                # Set the JWT token in the cookies
                # secure_cookie = settings.ENVIRONMENT == "production"
                # response.set_cookie("access_token", access_token, httponly=True, secure=secure_cookie, samesite="Lax")
                # response.set_cookie("refresh_token", str(refresh_token), httponly=True, secure=secure_cookie, samesite="Lax")
                return response
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]  # Extract the token after "Bearer "
    else:
        # 쿠키 방식 주석처리
        # If the header is not present, check the cookie for the access token
        # access_token = request.COOKIES.get("access_token")
        return JsonResponse({"error": "Token not found"}, status=status.HTTP_401_UNAUTHORIZED)

    access_token_obj = AccessToken(access_token)
    user_id = access_token_obj["user_id"]
    user = User.objects.get(user_id=user_id)
    request.user = user  # Attach user to request
    refresh_token = RefreshTokenModel.objects.filter(user_id=user_id, blacklisted=False).first()  # Ensure the refresh token is not blacklisted

    if refresh_token:
        try:
            token_instance = RefreshTokenModel.objects.get(token=refresh_token)
            token_instance.blacklist()
        except RefreshTokenModel.DoesNotExist:
            pass

    oauth_kakao_logout_view(request)
    logout(request)

    response = redirect("/")
    # 쿠키 방식 주석처리
    # response.delete_cookie("access_token")
    # response.delete_cookie("refresh_token")
    return response


class SignUpAPIView(APIView):
    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    @swagger_auto_schema(auto_schema=None)
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
    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        # 쿠키 방식 주석처리
        # refresh_token = request.COOKIES.get("refresh_token")
        refresh_token = request.headers.get("Authorization")  # 헤더에서 토큰을 가져오는 방식으로 변경
        if refresh_token:
            try:
                token_instance = RefreshTokenModel.objects.get(token=refresh_token)
                token_instance.blacklist()
            except RefreshTokenModel.DoesNotExist:
                pass

        logout(request)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        # 쿠키 방식 주석처리
        # response.delete_cookie("access_token")
        # response.delete_cookie("refresh_token")
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
    kakao_access_token = response_token["access_token"]
    kakao_refresh_token = response_token["refresh_token"]
    kakao_id_token = response_token.get("id_token")
    kakao_expires_in = response_token["refresh_token_expires_in"]
    kakao_expires_at = timezone.now() + timedelta(seconds=kakao_expires_in)

    response_oicd = call("GET", "https://kapi.kakao.com/v1/oidc/userinfo", {}, {"Authorization": f'Bearer {response_token["access_token"]}'})
    request.session["user_id"] = int(response_oicd["sub"])

    try:
        nickname = response_oicd["nickname"]
    except BaseException:
        nickname = response_oicd["sub"]

    try:
        photo = response_oicd["picture"]
    except BaseException:
        photo = None

    # Authenticate user
    user = authenticate(request, username=nickname, password="dummy")

    if user is None:
        # If user does not exist, create a new one
        user = User.objects.create_user(
            username=nickname, password="dummy", nickname=nickname, profile_photo=photo  # No password needed for OAuth login
        )

    # Blacklist all the existing, non-blacklisted tokens for the user
    RefreshTokenModel.objects.filter(user=user, blacklisted=False).update(blacklisted=True)

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
    access_token = str(RefreshToken(token_instance.token).access_token)

    # Create response to redirect to the main page
    response = redirect(reverse("index"))

    # 쿠키 방식 주석처리
    # Set the JWT token in the cookies
    # secure_cookie = settings.ENVIRONMENT == "production"
    # response.set_cookie("access_token", access_token, httponly=True, secure=secure_cookie, samesite="Lax")
    # response.set_cookie("refresh_token", str(refresh_token), httponly=True, secure=secure_cookie, samesite="Lax")
    return response


def oauth_kakao_logout_view(request):
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]  # Extract the token after "Bearer "
    else:
        # 쿠키 방식 주석처리
        # If the header is not present, check the cookie for the access token
        # access_token = request.COOKIES.get("access_token")
        return JsonResponse({"error": "Token not found"}, status=status.HTTP_401_UNAUTHORIZED)

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


class OauthKaKaoLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
        response_token = data["body"]
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
        try:
            nickname = response_oicd["nickname"]
        except BaseException:
            nickname = response_oicd["sub"]

        try:
            photo = response_oicd["picture"]
        except BaseException:
            photo = None

        # Authenticate user
        user = authenticate(request, username=nickname, password="dummy")

        if user is None:
            # If user does not exist, create a new one
            user = User.objects.create_user(
                username=nickname, password="dummy", nickname=nickname, profile_photo=photo  # No password needed for OAuth login
            )

        # Blacklist all the existing, non-blacklisted tokens for the user
        RefreshTokenModel.objects.filter(user=user, blacklisted=False).update(blacklisted=True)

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


@method_decorator(jwt_required, name="dispatch")
class OauthKaKaoLogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        access_token = request.access_token

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

        refresh_token = RefreshTokenModel.objects.filter(user_id=user_id, blacklisted=False).first()  # Ensure the refresh token is not blacklisted
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
        access_token = request.access_token

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


@method_decorator(jwt_required, name="dispatch")
class PreferenceAPIView(APIView):
    def post(self, request, *args, **kwargs):
        access_token = request.access_token

        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")

        # Retrieve the user from the database
        try:
            user = CustomUser.objects.get(user_id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get preference names from the request
        preference_names = request.data.get("preference", [])
        # Get all available keywords from the TourKeyword model
        all_keywords = TourKeyword.objects.all()

        for keyword in all_keywords:
            # If the current keyword name is in the provided preferences
            if keyword.keyword_name in preference_names:
                try:
                    # Add the preference to User_Preference
                    User_Preference.objects.create(user=user, preference=keyword)

                    # Update the rating: increase by 1 if matched
                    rating, created = KeywordRating.objects.get_or_create(user=user, keyword=keyword)

                    if not created:
                        rating.rating += 1
                    else:
                        rating.rating = 1  # Set to 1 if it's a new entry

                    rating.save()

                except TourKeyword.DoesNotExist:
                    return Response({"error": f"Preference '{keyword.keyword_name}' not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                # If the current keyword is NOT in the preferences, decrease the rating
                rating, created = KeywordRating.objects.get_or_create(user=user, keyword=keyword)

                if not created and rating.rating > 0:
                    rating.rating -= 1  # Decrease rating by 1 if it's already there and greater than 0
                    rating.save()

        response_data = {
            "statusCode": 200,
            "message": "OK",
            "content": {"message": "Preferences and ratings updated successfully.", "preference": preference_names},
        }

        # Return the response
        return Response(response_data, status=status.HTTP_200_OK)


class OauthUserCheckAPIView(APIView):
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
            response_token["refresh_token"]
            response_token.get("id_token")

            # Fetch user info from Kakao
            response_oicd = call("GET", "https://kapi.kakao.com/v1/oidc/userinfo", {}, {"Authorization": f"Bearer {kakao_access_token}"})

            try:
                nickname = response_oicd["nickname"]
            except BaseException:
                nickname = response_oicd["sub"]

            try:
                response_oicd["picture"]
            except BaseException:
                pass

            # Authenticate user
            user = authenticate(request, username=nickname, password="dummy")

            response_data = {
                "statusCode": 200,
                "message": "OK",
                "content": {
                    "user": (
                        {
                            "user_id": user.user_id,
                            "username": user.username,
                            "nickname": user.nickname,
                            "profile_photo": (user.profile_photo if user.profile_photo else None),
                        }
                        if user
                        else None
                    ),
                    "response_token": response_token,
                },
            }
            # Return the response
            return Response(response_data, status=status.HTTP_200_OK)

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SwaggerOauthKaKaoLoginAPIView(APIView):
    @swagger_auto_schema(auto_schema=None)
    def get(self, request):
        code = request.GET.get("code")
        data = {
            "grant_type": "authorization_code",
            "client_id": env("KAKAO_CLIENT_ID"),
            "redirect_uri": env("SWAGGER_KAKAO_REDIRECT_URI"),
            "code": code,
        }
        header = {"content-type": "application/x-www-form-urlencoded"}
        token_uri = "https://kauth.kakao.com/oauth/token"
        response_token = call("POST", token_uri, data, header)

        kakao_access_token = response_token["access_token"]
        kakao_refresh_token = response_token["refresh_token"]
        kakao_id_token = response_token.get("id_token")
        kakao_expires_in = response_token["refresh_token_expires_in"]
        kakao_expires_at = timezone.now() + timedelta(seconds=kakao_expires_in)

        response_oicd = call("GET", "https://kapi.kakao.com/v1/oidc/userinfo", {}, {"Authorization": f'Bearer {response_token["access_token"]}'})
        request.session["user_id"] = int(response_oicd["sub"])

        try:
            nickname = response_oicd["nickname"]
        except BaseException:
            nickname = response_oicd["sub"]

        try:
            photo = response_oicd["picture"]
        except BaseException:
            photo = None

        # Authenticate user
        user = authenticate(request, username=nickname, password="dummy")

        if user is None:
            # If user does not exist, create a new one
            user = User.objects.create_user(
                username=nickname, password="dummy", nickname=nickname, profile_photo=photo  # No password needed for OAuth login
            )

        # Blacklist all the existing, non-blacklisted tokens for the user
        RefreshTokenModel.objects.filter(user=user, blacklisted=False).update(blacklisted=True)

        user.oauth_kakao_access_token = kakao_access_token
        user.oauth_kakao_refresh_token = kakao_refresh_token
        user.oauth_kakao_id_token = kakao_id_token
        user.oauth_kakao_expires_at = kakao_expires_at
        user.save()
        # Log the user in
        login(request, user)
        # Issue JWT token
        token_instance = RefreshTokenModel.create_token(user)

        token_instance.token
        access_token = str(RefreshToken(token_instance.token).access_token)

        # Redirect to Swagger UI and pass the token in the query params
        swagger_ui_url = f"/swagger/?access_token={access_token}"
        return redirect(swagger_ui_url)
