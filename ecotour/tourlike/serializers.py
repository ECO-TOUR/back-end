from rest_framework import serializers
from community.models import Likes

class TourPlaceLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = ['tour_id', 'user_id', 'likes_id', 'likes_date']
