import uuid

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models


class User(AbstractUser):
    USER_CACHE_KEY = "{user_uuid}_access_token"
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)

    @property
    def get_user_token(self):
        # imported here due to circular import
        from users.helpers import generate_user_access_token

        cache_key = User.USER_CACHE_KEY.format(user_uuid=self.uuid)
        token = cache.get(key=cache_key)
        if not token:
            token = generate_user_access_token(user=self)
            cache.set(key=cache_key, value=token)

        return token
