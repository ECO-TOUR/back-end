# accounts/admin.py

from django.contrib import admin
from .models import RefreshTokenModel
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser


@admin.register(RefreshTokenModel)
class RefreshTokenModelAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "jti", "created_at", "expires_at", "blacklisted")
    search_fields = ("user__username", "token", "jti")
    list_filter = ("blacklisted", "created_at", "expires_at")


# Define a custom form for creating users
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "profile_photo",
            "nickname",
            "password1",
            "password2",
        )


# Define a custom form for changing user details
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "profile_photo", "nickname", "password")


# Extend the default UserAdmin to use the custom forms
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "nickname",
        "profile_photo",
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("profile_photo", "nickname")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("profile_photo", "nickname")}),
    )


# Register the custom user admin
admin.site.register(CustomUser, CustomUserAdmin)
