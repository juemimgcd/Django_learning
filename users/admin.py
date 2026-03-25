from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, UserLoginLog, UserToken


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "username", "nickname", "phone", "gender", "is_staff")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": ("nickname", "avatar", "gender", "bio", "phone"),
            },
        ),
    )


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token", "expires_at", "created_at")
    search_fields = ("user__username", "token")


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "login_date", "login_at")
    search_fields = ("user__username",)

