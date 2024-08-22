# serializers.py
from rest_framework import serializers

from .models import *


class ExampleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=True, max_length=100)


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["banner_title", "banner_url"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["post_id", "post_text", "user_id", "post_score", "post_img", "last_modified"]


class PostLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLog
        fields = ["log_id", "search_date", "search_text", "user_id"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ["comments_id", "user_id", "comments"]


class TourPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPlace
        fields = ["tour_id", "tour_name", "tour_summary"]


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Preference
        fields = ["user_id", "preference_id"]
