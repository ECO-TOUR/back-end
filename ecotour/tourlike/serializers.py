from community.models import Likes
from rest_framework import serializers


class TourPlaceLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ["tour_id", "user_id", "likes_id", "like_date"]
