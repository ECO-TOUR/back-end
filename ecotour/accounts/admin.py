# accounts/admin.py

from django.contrib import admin
from .models import RefreshTokenModel


@admin.register(RefreshTokenModel)
class RefreshTokenModelAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "jti", "created_at", "expires_at", "blacklisted")
    search_fields = ("user__username", "token", "jti")
    list_filter = ("blacklisted", "created_at", "expires_at")
