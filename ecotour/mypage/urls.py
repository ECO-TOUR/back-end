from django.urls import path

from . import views

app_name = "mypage"

urlpatterns = [path("api/<int:user_id>/inquire/", views.mypageInguireAPIView.as_view(), name="inquire")]
