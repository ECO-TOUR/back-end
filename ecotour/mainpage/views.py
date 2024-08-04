from community.models import Banner, TourPlace
from django.http import JsonResponse
from rest_framework import status

from .serializers import *


def banner(request):
    banner_list = Banner.objects.all()
    serializer = BannerSerializer(banner_list, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


# 인기 관광 5
def best(request):
    tour_list = TourPlace.objects.all().order_by("-tour_viewcnt_month")
    tour_list = tour_list[:5]
    serializer = TourPlaceSerializer(tour_list, many=True)

    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
