from django.urls import path

from . import views

urlpatterns = [
    path("place", views.search_tour_places, name="search_tour_places"),
    path("place/log/<int:user_id>/", views.get_search_history, name="get_search_history"),
    path("place/log/<int:user_id>/<int:log_id>/delete", views.delete_search_history, name="delete_search_history"),
    path("autocomplete/", views.autocomplete_search, name="autocomplete_search"),
    path("place/log/rank", views.get_top_search_terms, name="get_top_search_terms"),
    path("api/postbytour/<int:id>/", views.postbytour),
    path("place/detail/<int:tour_id>/", views.tour_place_detail, name="tour_place_detail"),  # 관광지 상세정보 URL 패턴 추가
]
