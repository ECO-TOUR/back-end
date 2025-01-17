from django.urls import path

from . import views

urlpatterns = [
    path("place", views.search_tour_places, name="search_tour_places"),
    path("place/log/<int:user_id>/", views.get_search_history, name="get_search_history"),
    path("place/log/<int:user_id>/<int:log_id>/delete", views.delete_search_history, name="delete_search_history"),
    path("autocomplete/", views.autocomplete_search, name="autocomplete_search"),
    path("place/log/rank", views.get_top_search_terms, name="get_top_search_terms"),
    path("api/postbytour/<int:id>/", views.postbytour),
    path("place/detail/<int:tour_id>/<int:user_id>/", views.tour_place_detail, name="tour_place_detail"),  # 사용자 ID를 포함한 관광지 상세정보 URL 패턴
    path("place/log/<int:user_id>/delete_all/", views.delete_all_search_history, name="delete_all_search_history"),
    path("Post/place/search/<int:user_id>/", views.post_search_tour_places, name="post_search_tour_places"), # 게시글 관광지 검색 URL 패턴 추가
]
