from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    profile_photo = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, unique=True)
    oauth_kakao_access_token = models.CharField(max_length=512, blank=True, null=True)
    oauth_kakao_refresh_token = models.CharField(max_length=512, blank=True, null=True)
    oauth_kakao_id_token = models.CharField(max_length=1024, blank=True, null=True)
    oauth_kakao_expires_at = models.DateTimeField(blank=True, null=True)  # Token expiration time

    def __str__(self):
        return self.username


class RefreshTokenModel(models.Model):
    token_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    jti = models.CharField(max_length=36, unique=True)  # JTI 필드 추가
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return self.token

    @staticmethod
    def create_token(user):
        refresh = RefreshToken.for_user(user)
        token_instance = RefreshTokenModel.objects.create(
            user=user, token=str(refresh), jti=refresh["jti"], expires_at=timezone.now() + refresh.lifetime
        )
        return token_instance

    def blacklist(self):
        self.blacklisted = True
        self.save()
