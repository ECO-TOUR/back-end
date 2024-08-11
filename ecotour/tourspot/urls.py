from django.urls import path
from . import views

urlpatterns = [
    path('place', views.search_tour_places, name='search_tour_places'),
    path('place/log/<int:user_id>/', views.get_search_history, name='get_search_history'),
    path('place/log/<int:user_id>/<int:log_id>/delete', views.delete_search_history, name='delete_search_history'),
    path('autocomplete/', views.autocomplete_search, name='autocomplete_search'),
    path('place/log/rank', views.get_top_search_terms, name='get_top_search_terms'),
]
