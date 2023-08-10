"""
This file contains all middlewares related to users application.
"""
import jwt
from django.contrib.auth import get_user_model
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)

User = get_user_model()


class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if token:
            private_key = open("jwtRS256.key.pub").read().encode()
            try:
                data = jwt.decode(
                    token.split()[1],
                    private_key,
                    algorithms=[
                        "RS256",
                    ],
                )
                request.user = User._default_manager.get(uuid=data["user_uuid"])
            except (
                ExpiredSignatureError,
                InvalidSignatureError,
                InvalidTokenError,
                User.DoesNotExist,
            ) as _error:
                pass

        response = self.get_response(request)

        return response
