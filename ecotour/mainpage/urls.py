from django.urls import path

from . import views
from .views import *

urlpatterns = [path("api/banner/", BannerView.as_view(), name="api_banner"), path("api/best/", views.best)]
