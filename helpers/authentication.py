"""
This file contains all middlewares related to users application.
"""
from os import environ

import jwt
from django.contrib.auth import get_user_model
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Backend authentication class for JWT based auth.
    """

    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "").split()
        if not auth or auth[0].lower() != "bearer":
            return None

        if len(auth) == 1:
            raise AuthenticationFailed("Invalid token header. No credentials provided.")
        elif len(auth) > 2:
            raise AuthenticationFailed(
                "Invalid token header. Token string should not contain spaces."
            )
        private_key = open(environ["JWT_DECRYPTION_KEY_PATH"]).read().encode()
        try:
            data = jwt.decode(
                auth[1],
                private_key,
                algorithms=[
                    "RS256",
                ],
            )
            user = User._default_manager.get(uuid=data["user_uuid"])
        except (ExpiredSignatureError, InvalidSignatureError, InvalidTokenError) as _error:
            raise AuthenticationFailed("Token signature expired. Please generate a new token.")
        except User.DoesNotExist as _error:
            raise AuthenticationFailed("No user exists with given token.")

        return (user, None)
