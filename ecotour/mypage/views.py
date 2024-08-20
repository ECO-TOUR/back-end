import jwt
from accounts.models import CustomUser
from common.decorators import jwt_required
from community.models import *
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *

User = get_user_model()


@method_decorator(jwt_required, name="dispatch")
class mypageInguireAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the user ID from the request (set by the jwt_required decorator)
        access_token = request.COOKIES.get("access_token")

        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])

        user_id = payload.get("user_id")

        # Retrieve the user from the database
        try:
            user = CustomUser.objects.get(user_id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "statusCode": 200,
            "message": "OK",
            "content": {
                "user": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "profile_photo": (user.profile_photo if user.profile_photo else None),
                }
            },
        }

        # Clear cookies
        response = Response(response_data, status=status.HTTP_200_OK)

        return response


def inquirenoti(request):
    noti_list = Notification.objects.all().order_by("-noti_date")
    serializer = NotiSerializer(noti_list, many=True)
    response_data = {"statusCode": "OK", "message": "OK", "content": serializer.data}

    return JsonResponse(response_data, status=status.HTTP_200_OK, safe=False)
