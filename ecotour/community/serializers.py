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
        fields = ["post_text", "post_score"]
