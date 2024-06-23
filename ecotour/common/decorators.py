from functools import wraps

from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError

User = get_user_model()


def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        access_token = request.COOKIES.get("access")
        refresh_token = request.COOKIES.get("refresh")
        if not access_token:
            return HttpResponseRedirect(reverse("accounts:login"))

        try:
            access_token_obj = AccessToken(access_token)
            user_id = access_token_obj["user_id"]
            user = User.objects.get(id=user_id)
            request.user = user
        except (TokenError, User.DoesNotExist):
            # Access token is invalid, try to use the refresh token to get a new access token
            if not refresh_token:
                return HttpResponseRedirect(reverse("accounts:login"))

            try:
                refresh_token_obj = RefreshToken(refresh_token)
                new_access_token = str(refresh_token_obj.access_token)
                user_id = refresh_token_obj["user_id"]
                user = User.objects.get(id=user_id)

                # Set the new access token in cookies
                response = HttpResponseRedirect(request.get_full_path())
                response.set_cookie("access", new_access_token, httponly=True, secure=False, samesite="Lax")
                request.user = user
                return response
            except TokenError:
                return HttpResponseRedirect(reverse("accounts:login"))

        return view_func(request, *args, **kwargs)

    return _wrapped_view
