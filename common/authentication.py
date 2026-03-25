from django.utils import timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from users.models import UserToken


class BearerTokenAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None

        if len(auth) == 1:
            token = auth[0].decode("utf-8")
        elif len(auth) == 2 and auth[0].decode("utf-8") == self.keyword:
            token = auth[1].decode("utf-8")
        else:
            raise AuthenticationFailed("Invalid token header.")

        token_record = (
            UserToken.objects.select_related("user")
            .filter(token=token, expires_at__gte=timezone.now())
            .first()
        )
        if token_record is None:
            raise AuthenticationFailed("Invalid or expired token.")

        return token_record.user, token_record

    def authenticate_header(self, request):
        return self.keyword
