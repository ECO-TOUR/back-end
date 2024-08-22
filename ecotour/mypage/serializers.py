from community.models import *
from rest_framework import serializers


class NotiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["noti_id", "noti_title", "noti_text", "noti_date"]
