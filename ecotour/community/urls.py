from django.urls import path
from .import views
from .views import *
urlpatterns = [
    path('test1/', Test1View.as_view(), name='test1'),
    path('test2/<int:id>/',Test2View.as_view(), name='test2'),
    path('test3/', views.test3),
    path('test4/', views.test4),
    path('search/', views.search),
    path('best/', views.best),
    path('example/', ExampleView.as_view(), name='example'),
]
