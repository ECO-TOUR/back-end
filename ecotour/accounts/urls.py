from django.urls import path

from .views import (
    LoginAPIView,
    LogoutAPIView,
    OauthKaKaoLoginAPIView,
    OauthKaKaoLogoutAPIView,
    OauthKaKaoSignoutAPIView,
    OauthUserCheckAPIView,
    PreferenceAPIView,
    SignUpAPIView,
    SwaggerOauthKaKaoLoginAPIView,
    authorize_code_kakao,
    login_view,
    logout_view,
    oauth_kakao_login_view,
    oauth_kakao_logout_view,
    signup_view,
)

app_name = "accounts"
urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("api/signup/", SignUpAPIView.as_view(), name="api_signup"),
    path("api/login/", LoginAPIView.as_view(), name="api_login"),
    path("api/logout/", LogoutAPIView.as_view(), name="api_logout"),
    path("authorize/code/kakao/", authorize_code_kakao, name="authorize_code_kakao"),
    path("oauth/kakao/login/", oauth_kakao_login_view, name="oauth_kakao_login"),
    path("oauth/kakao/logout/", oauth_kakao_logout_view, name="oauth_kakao_logout"),
    path("api/oauth/kakao/usercheck/", OauthUserCheckAPIView.as_view(), name="api_oauth_kakao_usercheck"),
    path("api/oauth/kakao/login/", OauthKaKaoLoginAPIView.as_view(), name="api_oauth_kakao_login"),
    path("api/oauth/kakao/login/swagger", SwaggerOauthKaKaoLoginAPIView.as_view(), name="api_oauth_kakao_login_swagger"),
    path("api/oauth/kakao/logout/", OauthKaKaoLogoutAPIView.as_view(), name="api_oauth_kakao_logout"),
    path("api/oauth/kakao/signout/", OauthKaKaoSignoutAPIView.as_view(), name="api_oauth_kakao_signout"),
    path("api/preference/", PreferenceAPIView.as_view(), name="api_preference"),
]
