from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed, AuthenticationFailed

from kanben.settings import TOKEN_EXPIRE_AFTER_SECONDS
from datetime import timedelta
import datetime, pytz

def utc_now():
	utc_now = datetime.datetime.utcnow()
	utc_now = utc_now.replace(tzinfo=pytz.utc)
	return utc_now


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        if token.created < utc_now() - timedelta(seconds=TOKEN_EXPIRE_AFTER_SECONDS):
            raise AuthenticationFailed('Token has expired')

        return token.user, token