from django.urls import path
from . import views

app_name = 'tourlikes'

urlpatterns = [
    path('wishlist/<int:user_id>/Inquire', views.liked_places, name='inquire'),
    path('wishlist/<int:user_id>/toggle', views.toggle_like, name='toggle'),
]
