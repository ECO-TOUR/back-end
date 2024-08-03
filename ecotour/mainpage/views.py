from community.models import Banner, TourPlace
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class BannerView(APIView):
    def get(self, request, format=None):
        banner_list = Banner.objects.all()
        serializer = BannerSerializer(banner_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 인기 관광 5
def best(request):
    tour_list = TourPlace.objects.all().order_by("-tour_viewcnt_month")
    tour_list = tour_list[:5]
    serializer = TourPlaceSerializer(tour_list, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
