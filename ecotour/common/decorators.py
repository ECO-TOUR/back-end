from functools import wraps

import jwt
from accounts.models import RefreshTokenModel
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError

User = get_user_model()


def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # First, check the Authorization header for the token
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]  # Extract the token after "Bearer "
            token_source = "header"
        else:
            # If the header is not present, check the cookie for the access token
            access_token = request.COOKIES.get("access_token")
            token_source = "cookie"
            if not access_token:
                # Handle JSON responses
                response = view_func(request, *args, **kwargs)
                if isinstance(response, JsonResponse):
                    return JsonResponse({"error": "Access token missing from both header and cookies"}, status=401)

                # Handle HTML/HTTP responses
                elif isinstance(response, HttpResponse):
                    return HttpResponseRedirect(reverse("accounts:login"))

        try:
            # Validate the access token

            access_token_obj = AccessToken(access_token)

            user_id = access_token_obj["user_id"]
            user = User.objects.get(user_id=user_id)
            request.user = user  # Attach user to request
            request.access_token = access_token

        except (TokenError, User.DoesNotExist):
            # If access token is invalid or expired, check for valid refresh token
            try:
                payload = jwt.decode(access_token, options={"verify_signature": False})  # 서명 및 만료 검증 비활성화

                user_id = payload.get("user_id")
                refresh_token_record = RefreshTokenModel.objects.filter(
                    user_id=user_id, blacklisted=False  # Ensure the refresh token is not blacklisted
                ).first()

                if not refresh_token_record:
                    response = view_func(request, *args, **kwargs)

                    if isinstance(response, JsonResponse):
                        return JsonResponse({"error": "No valid refresh token found, please log in again."}, status=401)
                    # Handle HTML/HTTP responses
                    elif isinstance(response, HttpResponse):
                        return HttpResponseRedirect(reverse("accounts:login"))

                # Use the refresh token to generate a new access token
                refresh_token_obj = RefreshToken(refresh_token_record.token)
                new_access_token = str(refresh_token_obj.access_token)
                user = User.objects.get(user_id=user_id)
                request.user = user  # Attach user to request
                request.access_token = new_access_token

                # Include the new access token based on where the original token came from
                if token_source == "header":
                    # Include the new access token in the response headers
                    request.META["HTTP_AUTHORIZATION"] = f"Bearer {new_access_token}"
                    response = view_func(request, *args, **kwargs)
                elif token_source == "cookie":
                    # Store the new access token in cookies
                    response = view_func(request, *args, **kwargs)
                    secure_cookie = settings.ENVIRONMENT == "production"
                    response.set_cookie("access_token", new_access_token, httponly=True, secure=secure_cookie, samesite="Lax")
                return response

            except (TokenError, User.DoesNotExist):
                return JsonResponse({"error": "Invalid refresh token, please log in again."}, status=401)

            # Execute the wrapped view function
        return view_func(request, *args, **kwargs)

    return _wrapped_view
