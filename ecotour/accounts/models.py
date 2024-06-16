from django.conf import settings
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta


class RefreshTokenModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.token

    @staticmethod
    def create_token(user):
        refresh = RefreshToken.for_user(user)
        token_instance = RefreshTokenModel.objects.create(
            user=user, token=str(refresh), expires_at=timezone.now() + refresh.lifetime
        )
        return token_instance
