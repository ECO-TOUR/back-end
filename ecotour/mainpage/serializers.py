# serializers.py
from community.models import *
from rest_framework import serializers


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["banner_title", "banner_url"]


class TourPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPlace
        fields = ["tour_viewcnt_month", "tour_id", "tour_name", "tour_location"]
