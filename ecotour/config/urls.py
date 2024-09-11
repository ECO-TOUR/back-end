"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from common.decorators import jwt_required
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


@jwt_required
def index(request):
    return render(request, "index.html")


schema_view = get_schema_view(
    openapi.Info(
        title="ECOTOUR",
        default_version="1.0.0",
        description="ECOTOUR",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="pby121@naver.com"),  # 부가정보
        license=openapi.License(name="BSD License"),  # 부가정보
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    # re_path(
    #     r"swagger/(?P<format>\.json|\.yaml)",
    #     schema_view.without_ui(cache_timeout=0),
    #     name="schema-json",
    # ),
    path("api/schema/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("swagger/", TemplateView.as_view(template_name="swagger-ui.html"), name="swagger-ui"),
    # path(
    #     "swagger/",
    #     schema_view.with_ui("swagger", cache_timeout=0),
    #     name="schema-swagger-ui",
    # ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc-v1"),
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("accounts/", include("accounts.urls")),
    # path("community/", include("community.urls")),
    path("mainpage/", include("mainpage.urls")),
    path("tourlike/", include("tourlike.urls")),
    path("community/", include("community.urls")),
    path("mypage/", include("mypage.urls")),
    path("", include("tourspot.urls")),
]
