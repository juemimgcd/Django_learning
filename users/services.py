from django.db import transaction
from django.utils import timezone

from .models import User, UserLoginLog, UserToken


def get_user_by_username(*, username):
    return User.objects.filter(username=username).first()


def create_user(*, validated_data):
    user = User.objects.create_user(
        username=validated_data["username"],
        password=validated_data["password"],
    )
    return user


def authenticate_user(*, username, password):
    user = get_user_by_username(username=username)
    if user is None or not user.check_password(password):
        return None
    return user


@transaction.atomic
def create_or_refresh_token(*, user):
    token = UserToken.generate_token()
    expires_at = UserToken.default_expiry()
    token_record, created = UserToken.objects.get_or_create(
        user=user,
        defaults={
            "token": token,
            "expires_at": expires_at,
        },
    )
    if not created:
        token_record.token = token
        token_record.expires_at = expires_at
        token_record.save(update_fields=["token", "expires_at"])

    return token_record


@transaction.atomic
def record_user_login(*, user):
    today = timezone.localdate()
    login_log, created = UserLoginLog.objects.get_or_create(
        user=user,
        login_date=today,
        defaults={"login_at": timezone.now()},
    )
    if not created:
        login_log.login_at = timezone.now()
        login_log.save(update_fields=["login_at"])
    return login_log


@transaction.atomic
def update_user(*, user, validated_data):
    for field, value in validated_data.items():
        setattr(user, field, value)
    user.save()
    return user


@transaction.atomic
def change_user_password(*, user, old_password, new_password):
    if not user.check_password(old_password):
        return False
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True

