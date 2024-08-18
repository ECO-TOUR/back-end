from community.models import Likes, TourPlace
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
User = get_user_model()


# @login_required
def toggle_like(request, user_id):
    if request.method == "POST":
        tour_id = request.POST.get("tour_id")
        tour_place = get_object_or_404(TourPlace, tour_id=tour_id)
        user = get_object_or_404(User, user_id=user_id)
        like, created = Likes.objects.get_or_create(user_id=user, tour_id=tour_place)
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
# @login_required
def liked_places(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    likes = Likes.objects.filter(user_id=user)
    likes_list = [{"tour_id": like.tour_id.id, "tour_name": like.tour_id.tour_name} for like in likes]
    return JsonResponse({"statusCode": 200, "message": "찜목록을 성공적으로 가져왔습니다.", "data": likes_list}, safe=False)
