from community.models import Post, TourLog, TourPlace
from community.serializers import *
from django.db.models import Avg, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import logging


# 관광지 검색
@csrf_exempt
def search_tour_places(request):
    if request.method == "GET":
        search_term = request.GET.get("search", "").strip()
        if not search_term:
            return JsonResponse({"statusCode": 400, "message": "검색어가 유효하지 않습니다."}, status=400)

        # 관광지 검색어와 일치하는 관광지 찾기
        matching_places = TourPlace.objects.filter(tour_name__icontains=search_term)

        # 관광지의 search_count 증가
        TourPlace.objects.filter(tour_name__icontains=search_term).update(search_count=F("search_count") + 1)

        # 검색어를 TourLog에 저장
        if request.user.is_authenticated:
            # 검색어와 일치하는 관광지의 tour_id 찾기
            matching_place_ids = matching_places.values_list('tour_id', flat=True)
            tour_id = matching_place_ids[0] if matching_place_ids else None

            TourLog.objects.create(user=request.user, search_text=search_term, tour_id=tour_id)

        # 관광지 검색 결과 파싱 및 반환
        search_results = []
        for place in matching_places:
            avg_score = Post.objects.filter(tour_id=place.tour_id).aggregate(Avg("post_score"))["post_score__avg"] or 0
            search_count = TourLog.objects.filter(search_text=search_term).count()

            search_results.append(
                {
                    "tour_id": place.tour_id,
                    "tour_name": place.tour_name,
                    "tour_img": place.tour_img,
                    "tour_location": place.tour_location,
                    "tour_viewcnt": place.tour_viewcnt,
                    "avg_score": avg_score,
                    "search_count": search_count,
                }
            )

        return JsonResponse({"statusCode": 200, "search_results": search_results}, status=200)

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)


# 관광지 상세정보
@csrf_exempt
def tour_place_detail(request, tour_id):
    if request.method == "GET":
        # 관광지 상세정보 조회
        place = get_object_or_404(TourPlace, tour_id=tour_id)

        # 관광지 조회수 증가
        place.tour_viewcnt += 1
        place.save()

        # 별점 계산
        avg_score = Post.objects.filter(tour_id=tour_id).aggregate(Avg("post_score"))["post_score__avg"] or 0

        # 게시물 정보 조회
        posts = Post.objects.filter(tour_id=tour_id).select_related("user")

        # 게시물 정보 구성
        post_details = [
            {
                "post_id": post.post_id,  # 게시물 ID
                "post_text": post.post_text,  # 게시물 내용
                "user_id": post.user_id,  # 사용자 ID
                "post_score": avg_score,  # 게시물 점수
                "post_img": post.post_img,  # 게시물 이미지 URL
                "last_modified": post.last_modified.isoformat(),  # 마지막 수정 시간
            }
            for post in posts
        ]

        # 빈 문자열을 None으로 변환하는 함수
        def empty_to_none(value):
            return None if value == "" else value

        # 상세정보 및 게시물 반환
        place_detail = {
            "tour_id": place.tour_id,
            "tour_name": place.tour_name,
            "tour_location": place.tour_location,
            "tour_img": place.tour_img,
            "tour_viewcnt": place.tour_viewcnt,
            "tour_summary": place.tour_summary,
            "tour_tel": empty_to_none(place.tour_tel),
            "tour_telname": empty_to_none(place.tour_telname),
            "tour_title": empty_to_none(place.tour_title),
            "opening_hours": empty_to_none(place.opening_hours),
            "tour_hours": empty_to_none(place.tour_hours),
            "website": empty_to_none(place.website),
            "fees": empty_to_none(place.fees),
            "restrooms": empty_to_none(place.restrooms),
            "parking": empty_to_none(place.parking),
            "avg_score": avg_score,
            "posts": post_details,
        }

        return JsonResponse({"statusCode": 200, "place_detail": place_detail}, status=200)

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)


# 사용자별 검색 기록 조회
logger = logging.getLogger(__name__)

@csrf_exempt
def get_search_history(request, user_id):
    if request.method == "GET":
        try:
            search_history = TourLog.objects.filter(user_id=user_id).order_by("-search_date")

            history = [
                {
                    "log_id": log.log_id,
                    "tour_id": log.tour_id,  # 투어 ID 참조 수정
                    "search_text": log.search_text,
                    "search_date": log.search_date.isoformat()
                }
                for log in search_history
            ]

            return JsonResponse({"statusCode": 200, "search_history": history}, status=200)

        except Exception as e:
            logger.error(f"Error fetching search history for user {user_id}: {str(e)}")
            return JsonResponse({"statusCode": 500, "message": "서버 오류입니다.", "error": str(e)}, status=500)

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)

# 검색 기록 전체 삭제
@csrf_exempt
def delete_all_search_history(request, user_id):
    if request.method == "DELETE":
        try:
            # 해당 사용자의 모든 검색 기록 삭제
            TourLog.objects.filter(user_id=user_id).delete()
            return JsonResponse({"statusCode": 200, "message": "모든 검색 기록이 삭제되었습니다."}, status=200)

        except Exception as e:
            logger.error(f"Error deleting search history for user {user_id}: {str(e)}")
            return JsonResponse({"statusCode": 500, "message": "서버 오류입니다.", "error": str(e)}, status=500)

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 DELETE여야 합니다."}, status=400)


# 검색 기록 삭제
@csrf_exempt
def delete_search_history(request, user_id, log_id):
    if request.method == "DELETE":
        # 해당 사용자와 일치하는 특정 검색 기록 삭제
        log = get_object_or_404(TourLog, log_id=log_id, user_id=user_id)
        log.delete()
        return JsonResponse({"statusCode": 200, "message": "검색 기록이 삭제되었습니다."})

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 DELETE여야 합니다."}, status=400)


# 검색어 순위
@csrf_exempt
def get_top_search_terms(request):
    if request.method == "GET":
        # 상위 10개의 관광지 검색어 순위 조회 (search_count 기준으로)
        top_places = TourPlace.objects.order_by("-search_count")[:10]
        top_searches = [
            {
                "tour_id": place.tour_id,  # 투어 ID 추가
                "tour_name": place.tour_name, 
                "search_count": place.search_count
            } 
            for place in top_places
        ]

        return JsonResponse({"statusCode": 200, "top_search_terms": top_searches})

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)


# 검색어 자동완성
def autocomplete_search(request):
    if request.method == "GET":
        query = request.GET.get("query", "")
        if query:
            autocomplete_results = TourPlace.objects.filter(tour_name__icontains=query).values_list("tour_name", flat=True)
            return JsonResponse({"statusCode": 200, "autocompleteResults": list(autocomplete_results)})
        else:
            return JsonResponse({"statusCode": 200, "autocompleteResults": []})

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)


def postbytour(request, id):
    post_list = Post.objects.filter(tour_id=id)

    serializer = PostSerializer(post_list, many=True)
    summ = 0
    cnt = 0
    for post in post_list:
        cnt += 1
        summ += post.post_score

    response_data = {"statusCode": "OK", "message": "OK", "content": {"data": serializer.data, "avg_score": summ / cnt, "count": cnt}}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)
