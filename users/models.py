from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.cache import cache
from django.db import models

from helpers.managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    USER_CACHE_KEY = "{user_uuid}_access_token"
    email = models.EmailField(unique=True)
    uuid = models.UUIDField(unique=True, default=uuid4, primary_key=True)
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
        verbose_name="staff status",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
        verbose_name="active",
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text="Designates that this user has all permissions without explicitly assigning them.",
        verbose_name="superuser status",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

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
