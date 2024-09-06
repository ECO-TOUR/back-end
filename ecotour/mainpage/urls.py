from django.urls import path

from . import views

urlpatterns = [
    path("api/banner/", views.banner, name="api_banner"),
    path("api/best/", views.best),
    path("api/viewcntmonth/", views.viewcntmonth),
    path("api/recommend/<int:id>/", views.recommendation),
]
