from common.recommend import recommend
from community.models import Banner, TourPlace
from django.db.models import Avg
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status

from .serializers import *


def banner(request):
    try:
        currenttime = timezone.now()

        # 데이터베이스 레벨에서 필터링 수행
        banner_list = Banner.objects.filter(startdate__lte=currenttime, enddate__gte=currenttime)

        # 시리얼라이저 사용하여 직렬화
        serializer = BannerSerializer(banner_list, many=True)

        # JSON 응답 반환
        # return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        response_data = {"statusCode": "OK", "message": "OK", "content": serializer.data}

        return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

    except Exception as e:
        # 예외 처리
        print(f"An error occurred: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 인기 관광 5
def best(request):
    tour_list = TourPlace.objects.all().order_by("-tour_viewcnt_month")
    tour_list = tour_list[:5]
    serializer = TourPlaceSerializer(tour_list, many=True)

    # return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    response_data = {"statusCode": "OK", "message": "OK", "content": serializer.data}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)


def viewcntmonth(request):
    try:
        # 필요한 필드만 가져오는 쿼리셋 최적화
        tour_list = TourPlace.objects.all()

        # 각 TourPlace 객체의 조회수를 업데이트
        for tour in tour_list:
            tour.tour_viewcnt += tour.tour_viewcnt_month
            tour.tour_viewcnt_month = 0
            tour.save()

        # return JsonResponse("OK", safe=False, status=status.HTTP_200_OK)

        response_data = {"statusCode": "OK", "message": "OK", "content": "OK"}

        return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)

    except Exception as e:
        # 예외 처리
        print(f"An error occurred: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred."}, safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calscore(tour_list):
    for x in tour_list:
        # tour_id에 해당하는 post_score의 평균을 계산 (None 처리 포함)
        score = Post.objects.filter(tour_id=x["tour_id"]).aggregate(avg_score=Avg("post_score"))["avg_score"] or 0
        # tour_id에 해당하는 post의 수를 계산
        count = Post.objects.filter(tour_id=x["tour_id"]).count()

        # 결과를 tour_list에 추가
        x["score"] = score
        x["count"] = count
    return tour_list


def recommendation(request, id):
    # Get the recommended tours
    tours_list = recommend(id)

    # Convert to a list of dictionaries (already a list in this case)
    tours_list = list(tours_list)

    # Calculate score and count for each tour
    tours_list = calscore(tours_list)

    response_data = {"statusCode": "OK", "message": "OK", "content": tours_list}
    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)
