from rest_framework import serializers
# from .models import Likes 보영 코드

class TourPlaceLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ['tour_id', 'user_id', 'likes_id', 'likes_date']
