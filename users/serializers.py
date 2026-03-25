from rest_framework import serializers

from .models import User


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "avatar",
            "gender",
            "bio",
            "phone",
        ]


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("user already exists")
        return value


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)


class UserUpdateSerializer(serializers.Serializer):
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    avatar = serializers.URLField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_phone(self, value):
        if value == "":
            return None

        user = self.context.get("user")
        queryset = User.objects.filter(phone=value)
        if user is not None:
            queryset = queryset.exclude(pk=user.pk)
        if queryset.exists():
            raise serializers.ValidationError("phone already exists")
        return value


class UserChangePasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(source="old_password", write_only=True, min_length=6)
    newPassword = serializers.CharField(source="new_password", write_only=True, min_length=6)


class UserAuthResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    expiresAt = serializers.DateTimeField(source="expires_at")
    userInfo = UserInfoSerializer(source="user")

