import json

from community.models import KeywordRating, Likes, TourPlace, TourPlace_TourKeyword
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


@csrf_exempt
def toggle_like(request, user_id):
    if request.method == "POST":
        data = json.loads(request.body)
        tour_id = data.get("tour_id")

        # 관광지 및 사용자 조회
        tour_place = get_object_or_404(TourPlace, tour_id=tour_id)
        user = get_object_or_404(User, user_id=user_id)

        # TourPlace_has_TourKeyword 테이블에서 keyword_id 찾기
        tour_keywords = TourPlace_TourKeyword.objects.filter(tour=tour_place)

        if not tour_keywords.exists():
            return JsonResponse({"statusCode": 404, "message": "관광지와 관련된 키워드를 찾을 수 없습니다."}, status=404)

        # 좋아요 처리
        like, created = Likes.objects.get_or_create(user=user, tour=tour_place)

        if not created:
            # 이미 좋아요를 누른 경우, 좋아요 취소
            like.delete()

            # 모든 관련 keyword_id에 대해 rating -1
            for tour_keyword in tour_keywords:
                keyword_rating, _ = KeywordRating.objects.get_or_create(user=user, keyword=tour_keyword.keyword)
                keyword_rating.rating = max(keyword_rating.rating - 1, 0)  # rating이 0보다 작아지지 않도록 설정
                keyword_rating.save()

            return JsonResponse(
                {
                    "statusCode": 200,
                    "message": "찜목록에서 관광지가 삭제되었습니다.",
                    "status": "unliked",
                    "tour_id": tour_id,
                    "tour_name": tour_place.tour_name,
                }
            )

        # 좋아요 추가
        for tour_keyword in tour_keywords:
            keyword_rating, _ = KeywordRating.objects.get_or_create(user=user, keyword=tour_keyword.keyword)
            keyword_rating.rating += 1
            keyword_rating.save()

        return JsonResponse(
            {
                "statusCode": 200,
                "message": "찜목록에서 관광지가 추가되었습니다.",
                "status": "liked",
                "tour_id": tour_id,
                "tour_name": tour_place.tour_name,
            }
        )
    return JsonResponse({"statusCode": 400, "message": "잘못된 요청입니다.", "error": "요청 메소드는 POST여야 합니다."}, status=400)


@csrf_exempt
def liked_places(request, user_id):
    try:
        # 특정 사용자가 찜한 관광지 목록 조회
        liked_places = Likes.objects.filter(user_id=user_id).select_related("tour")

        # 사용자가 찜한 관광지가 없을 경우 400 오류 반환
        if not liked_places.exists():
            return JsonResponse([], safe=False, status=200)

        # 각 관광지에 대한 평균 점수 계산
        results = []
        for like in liked_places:
            tour = like.tour
            # 특정 관광지와 연결된 게시글들의 평균 점수를 계산
            avg_post_score = tour.tourplacepost.aggregate(Avg("post_score"))["post_score__avg"] or 0
            results.append(
                {
                    "likes_id": like.likes_id,
                    "tour_id": tour.tour_id,
                    "tour_name": tour.tour_name,
                    "tour_img": tour.tour_img,
                    "tour_location": tour.tour_location,
                    "tour_viewcnt": tour.tour_viewcnt,
                    "avg_post_score": avg_post_score,  # 평균 점수가 없으면 0으로 설정
                }
            )

        return JsonResponse(results, safe=False)

    except ObjectDoesNotExist:
        # 요청된 데이터가 존재하지 않을 경우 400 오류 반환
        return JsonResponse({"error": "잘못된 요청입니다. 데이터를 찾을 수 없습니다."}, status=400)

    except Exception as e:
        # 기타 서버 오류 발생 시 500 오류 반환
        return JsonResponse({"error": "예상치 못한 오류가 발생했습니다.", "details": str(e)}, status=500)
