from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class CustomBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return AnonymousUser()

        try:
            user = User._default_manager.get(email=email)
        except User.DoesNotExist:
            return

        if user.check_password(password) and user.is_active:
            return user
