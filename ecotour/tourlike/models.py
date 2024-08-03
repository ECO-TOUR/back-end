from django.db import models
from django.contrib.auth.models import User
# from ecotour.models import TourPlace 보영 db
import uuid

class Likes(models.Model):
    likes_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # 좋아요 고유 번호
    likes_date = models.DateTimeField(auto_now_add=True)  # 좋아요한 날짜
    tour_id = models.ForeignKey(TourPlace, on_delete=models.CASCADE)  # 관광지 번호 (FK)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)  # 유저 번호 (FK)

    def __str__(self):
        return f"{self.user_id.username} likes {self.tour_id.tour_name}"
