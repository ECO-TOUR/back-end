import logging

import jwt
from accounts.models import CustomUser
from community.models import Post, TourLog, TourPlace
from community.serializers import *
from django.db.models import Avg, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status


# 관광지 검색
@csrf_exempt
def search_tour_places(request):
    if request.method == "GET":
        search_term = request.GET.get("search", "").strip()
        if not search_term:
            return JsonResponse({"statusCode": 400, "message": "검색어가 유효하지 않습니다."}, status=400)

        # 관광지 검색어와 일치하는 관광지 찾기
        matching_places = TourPlace.objects.filter(tour_name__icontains=search_term)

        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]  # Bearer 뒤의 토큰 값만 추출
        else:
            return JsonResponse({"statusCode": 401, "message": "인증 토큰이 없습니다."}, status=401)  # 바뀐 부분

        # JWT 디코딩 및 사용자 ID 추출
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({"statusCode": 401, "message": "토큰이 만료되었습니다."}, status=401)  # 바뀐 부분
        except jwt.InvalidTokenError:
            return JsonResponse({"statusCode": 401, "message": "유효하지 않은 토큰입니다."}, status=401)  # 바뀐 부분

        user_id = payload.get("user_id")

        # Retrieve the user from the database
        try:
            user = CustomUser.objects.get(user_id=user_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({"statusCode": 404, "message": "User not found"}, status=404)  # 바뀐 부분

        matching_place_ids = matching_places.values_list("tour_id", flat=True)
        tour_id = matching_place_ids[0] if matching_place_ids else None

        # 검색어를 TourLog에 저장
        TourLog.objects.create(user=user, search_text=search_term, tour_id=tour_id)

        # 관광지 검색 결과 파싱 및 반환
        search_results = []
        for place in matching_places:
            avg_score = Post.objects.filter(tour_id=place.tour_id).aggregate(Avg("post_score"))["post_score__avg"] or 0
            search_count = TourLog.objects.filter(search_text=search_term).count()

            user_liked = "liked" if user_id and Likes.objects.filter(user_id=user_id, tour_id=place.tour_id).exists() else "unliked"

            search_results.append(
                {
                    "tour_id": place.tour_id,
                    "tour_name": place.tour_name,
                    "tour_img": place.tour_img,
                    "tour_location": place.tour_location,
                    "tour_viewcnt": place.tour_viewcnt,
                    "avg_score": avg_score,
                    "search_count": search_count,
                    "tourspot_liked": user_liked,
                }
            )

        return JsonResponse({"statusCode": 200, "search_results": search_results}, status=200)

    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 GET이어야 합니다."}, status=400)


# 관광지 상세정보
@csrf_exempt
def tour_place_detail(request, tour_id, user_id=None):
    if request.method == "GET":
        # 관광지 상세정보 조회
        place = get_object_or_404(TourPlace, tour_id=tour_id)

        search_term = request.GET.get("search", "").strip()
        # 관광지의 search_count 증가
        TourPlace.objects.filter(tour_name__icontains=search_term).update(search_count=F("search_count") + 1)

        # 관광지 조회수 증가
        place.tour_viewcnt += 1
        place.save()

        # 별점 계산
        avg_score = Post.objects.filter(tour_id=tour_id).aggregate(Avg("post_score"))["post_score__avg"] or 0

        # 게시물 정보 조회
        posts = Post.objects.filter(tour_id=tour_id).select_related("user")

        # 빈 문자열 또는 None을 "정보없음"으로 변환하는 함수
        def value_or_info(value):
            return "정보 없음" if not value else value

        # 게시물 정보 구성
        post_details = [
            {
                "post_id": post.post_id,  # 게시물 ID
                "post_text": post.post_text,  # 게시물 내용
                "user_id": post.user_id,  # 사용자 ID
                "post_score": post.post_score,  # 게시물 점수 (각 게시물의 점수)
                "post_img": post.post_img if post.post_img else None,  # 게시물 이미지 URL (이미지가 있는 경우만)
                "last_modified": post.last_modified.isoformat() if post.last_modified else None,  # 마지막 수정 시간
            }
            for post in posts
        ]

        # 사용자가 해당 관광지를 찜했는지 확인
        user_liked = "liked" if user_id and Likes.objects.filter(user_id=user_id, tour_id=tour_id).exists() else "unliked"

        # 상세정보 및 게시물 반환
        place_detail = {
            "tour_id": place.tour_id,
            "tour_name": value_or_info(place.tour_name),
            "tour_location": value_or_info(place.tour_location),
            "tour_img": place.tour_img if place.tour_img else None,  # 이미지가 있는 경우만
            "tour_viewcnt": place.tour_viewcnt,
            "tour_summary": value_or_info(place.tour_summary),
            "tour_tel": value_or_info(place.tour_tel),
            "tour_telname": value_or_info(place.tour_telname),
            "tour_title": value_or_info(place.tour_title),
            "opening_hours": value_or_info(place.opening_hours),
            "tour_hours": value_or_info(place.tour_hours),
            "website": value_or_info(place.website),
            "fees": value_or_info(place.fees),
            "restrooms": value_or_info(place.restrooms),
            "parking": value_or_info(place.parking),
            "avg_score": avg_score,  # 평균 점수
            "posts": post_details,
            "tourspot_liked": user_liked,  # 찜 여부
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
                    "search_date": log.search_date.isoformat(),
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
            {"tour_id": place.tour_id, "tour_name": place.tour_name, "search_count": place.search_count} for place in top_places  # 투어 ID 추가
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
    cnt = len(post_list)  # post_list의 개수를 바로 cnt에 할당

    # post_score 합산
    for post in post_list:
        summ += post.post_score

    # cnt가 0일 경우 avg_score는 0으로 처리
    avg_score = summ / cnt if cnt > 0 else 0

    response_data = {"statusCode": "OK", "message": "OK", "content": {"data": serializer.data, "avg_score": avg_score, "count": cnt}}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)
