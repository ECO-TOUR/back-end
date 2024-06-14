from django.shortcuts import render
from django.http import HttpResponse
from .models import Banner
# Create your views here.

def test1(request):
    banner_list = Banner.objects.all()
    titles = ""
    for ban in banner_list:
        titles += ban.banner_title  # 수정된 부분: ban.title -> ban.banner_title
    return HttpResponse(titles)
