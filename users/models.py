import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_UNKNOWN = "unknown"
    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_UNKNOWN, "Unknown"),
    ]

    nickname = models.CharField(max_length=50, blank=True, default="")
    avatar = models.URLField(
        max_length=255,
        blank=True,
        default="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default=GENDER_UNKNOWN,
    )
    bio = models.CharField(max_length=500, blank=True, default="这个人很懒，什么都没留下")
    phone = models.CharField(max_length=20, blank=True, null=True, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["username"], name="users_username_idx"),
            models.Index(fields=["phone"], name="users_phone_idx"),
        ]


class UserToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="token_record",
    )
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["token"], name="users_token_idx"),
            models.Index(fields=["user"], name="users_token_user_idx"),
        ]

    @staticmethod
    def generate_token():
        return str(uuid.uuid4())

    @staticmethod
    def default_expiry():
        return timezone.now() + timedelta(days=7)


class UserLoginLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_logs",
    )
    login_date = models.DateField(default=timezone.localdate)
    login_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "login_date"], name="users_login_unique")
        ]
        indexes = [
            models.Index(fields=["user"], name="users_login_user_idx"),
            models.Index(fields=["login_date"], name="users_login_date_idx"),
        ]

