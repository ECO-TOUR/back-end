from django.urls import path

from . import views

urlpatterns = [
    # path("api/test1/", Test1View.as_view(), name="api_test1"),
    # path("api/postbyid/<int:id>/", views.postbyid),
    path("api/tourkeyword/", views.tourkeyword),
    path("api/place2keyword/<int:id>/", views.place2keyword),
    path("api/search/", views.search),
    path("api/postinquire/<int:id>/", views.postlist),
    path("api/postbest/", views.best),
    path("api/userpre/<int:id>/", views.userpre),
    path("api/postwrite/", views.write, name="api_write"),
    path("api/postmodify/", views.modify, name="api_modify"),
    path("api/postdelete/<int:id>/", views.delete, name="api_delete"),
    path("api/postsearch/<int:sorttype>/<str:text>/", views.search_post, name="api_search"),
    path("api/mypost/<int:id>/", views.mypost, name="api_mypost"),
    path("api/commentinquire/<int:id>/", views.comment, name="api_comments"),
    path("api/commentwrite/", views.comment_write, name="api_commentswrite"),
    # path('example/', ExampleView.as_view(), name='example'),
    path("api/postlogdelete/<int:id>/", views.deletepostlog),
    path("api/mypostlog/<int:id>/", views.mypostlog),
]
