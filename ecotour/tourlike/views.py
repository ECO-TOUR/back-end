import json
from django.shortcuts import get_object_or_404
from community.models import Likes, TourPlace
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


# @login_required
@csrf_exempt
def toggle_like(request, user_id):
    if request.method == "POST":
        data = json.loads(request.body)
        tour_id = data.get("tour_id")
        tour_place = get_object_or_404(TourPlace, tour_id=tour_id)
        user = get_object_or_404(User, user_id=user_id)
        like, created = Likes.objects.get_or_create(user=user, tour=tour_place)
        if not created:
            # 이미 좋아요를 누른 경우, 좋아요 취소
            like.delete()
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
        liked_places = Likes.objects.filter(user_id=user_id).select_related('tour')

        # 사용자가 찜한 관광지가 없을 경우 400 오류 반환
        if not liked_places.exists():
            return JsonResponse({"error": "해당 사용자가 찜한 관광지를 찾을 수 없습니다."}, status=400)

        # 각 관광지에 대한 평균 점수 계산
        results = []
        for like in liked_places:
            tour = like.tour
            # 특정 관광지와 연결된 게시글들의 평균 점수를 계산
            avg_post_score = tour.tourplacepost.aggregate(Avg('post_score'))['post_score__avg'] or 0
            results.append({
                "likes_id": like.likes_id,
                "tour_id": tour.tour_id,
                "tour_name": tour.tour_name,
                "tour_img": tour.tour_img,
                "tour_location": tour.tour_location,
                "tour_viewcnt": tour.tour_viewcnt,
                "avg_post_score": avg_post_score,  # 평균 점수가 없으면 0으로 설정
            })

        return JsonResponse(results, safe=False)

    except ObjectDoesNotExist:
        # 요청된 데이터가 존재하지 않을 경우 400 오류 반환
        return JsonResponse({"error": "잘못된 요청입니다. 데이터를 찾을 수 없습니다."}, status=400)

    except Exception as e:
        # 기타 서버 오류 발생 시 500 오류 반환
        return JsonResponse({"error": "예상치 못한 오류가 발생했습니다.", "details": str(e)}, status=500)
