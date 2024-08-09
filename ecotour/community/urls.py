from django.urls import path

from . import views
from .views import *

urlpatterns = [
    # path("api/test1/", Test1View.as_view(), name="api_test1"),
    path("api/postbyid/<int:id>/", views.postbyid),
    path("api/tourkeyword/", views.tourkeyword),
    path("api/place2keyword/<int:id>", views.place2keyword),
    path("api/search/", views.search),
    path("api/search2/<int:id>", views.search2),
    path("api/best/", views.best),
    path("api/userpre/<int:id>", views.userpre),
    path("api/write/", WriteView.as_view(), name="api_write"),
    path("api/modify/", ModifyView.as_view(), name="api_modify"),
    path("api/delete/<int:id>/", DeleteView.as_view(), name="api_delete"),
    path("api/search/<int:sorttype>/<str:text>", SearchView.as_view(), name="api_search"),
    path("api/mypost/<int:id>/", MyPostView.as_view(), name="api_mypost"),
    path("api/comment/<int:post_id>/", CommentsView.as_view(), name="api_comments"),
    path("api/commentwrite/", CommentsWriteView.as_view(), name="api_commentswrite"),
    # path('example/', ExampleView.as_view(), name='example'),
]