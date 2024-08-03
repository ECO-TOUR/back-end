from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path("api/test1/", Test1View.as_view(), name="api_test1"),
    path("api/test2/<int:id>/", Test2View.as_view(), name="api_test2"),
    path("test3/", views.test3),
    path("test4/", views.test4),
    path("search/", views.search),
    path("search2/", views.search2),
    path("best/", views.best),
    path("userpre/", views.userpre),
    path("api/write/", WriteView.as_view(), name="api_write"),
    path("api/modify/", ModifyView.as_view(), name="api_modify"),
    path("api/delete/<int:id>/", DeleteView.as_view(), name="api_delete"),
    path("api/search/<int:sorttype>/<str:text>", SearchView.as_view(), name="api_search"),
    path("api/mypost/<int:id>/", MyPostView.as_view(), name="api_mypost"),
    path("api/comment/<int:post_id>/", CommentsView.as_view(), name="api_comments"),
    path("api/commentwrite/", CommentsWriteView.as_view(), name="api_commentswrite"),
    # path('example/', ExampleView.as_view(), name='example'),
]
