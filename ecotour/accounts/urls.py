from django.urls import path

from .views import LoginAPIView, LogoutAPIView, SignUpAPIView, login_view, logout_view, signup_view

app_name = "accounts"
urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("api/signup/", SignUpAPIView.as_view(), name="api_signup"),
    path("api/login/", LoginAPIView.as_view(), name="api_login"),
    path("api/logout/", LogoutAPIView.as_view(), name="api_logout"),
]
