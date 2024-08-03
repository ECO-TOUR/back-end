from django.urls import path
from . import views

# app_name = 'tourlike'

urlpatterns = [
    # path('api/wishlist/<int:user_id>/Inquire/', views.liked_places, name='inquire'),
    path('api/wishlist/<int:user_id>/toggle/', views.toggle_like, name='toggle'),
]
