from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.authentication import BearerTokenAuthentication
from common.responses import success_response

from .serializers import (
    UserAuthResponseSerializer,
    UserChangePasswordSerializer,
    UserInfoSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
)
from .services import (
    authenticate_user,
    change_user_password,
    create_or_refresh_token,
    create_user,
    record_user_login,
    update_user,
)


class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = create_user(validated_data=serializer.validated_data)
        token_record = create_or_refresh_token(user=user)
        record_user_login(user=user)

        output = UserAuthResponseSerializer(
            {
                "token": token_record.token,
                "expires_at": token_record.expires_at,
                "user": user,
            }
        )
        return success_response(data=output.data)


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate_user(**serializer.validated_data)
        if user is None:
            raise ValidationError("wrong username or password")

        token_record = create_or_refresh_token(user=user)
        record_user_login(user=user)

        output = UserAuthResponseSerializer(
            {
                "token": token_record.token,
                "expires_at": token_record.expires_at,
                "user": user,
            }
        )
        return success_response(data=output.data)


class UserInfoAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(message="获取用户信息成功", data=UserInfoSerializer(request.user).data)


class UserUpdateAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(data=request.data, context={"user": request.user})
        serializer.is_valid(raise_exception=True)

        user = update_user(user=request.user, validated_data=serializer.validated_data)
        return success_response(data=UserInfoSerializer(user).data)


class UserPasswordAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        changed = change_user_password(user=request.user, **serializer.validated_data)
        if not changed:
            raise ValidationError("wrong old password")

        return success_response()
