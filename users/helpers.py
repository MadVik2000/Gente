"""
This file contains all the helpers related to users application.
"""

from os import environ

import jwt
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta

User = get_user_model()


def generate_user_access_token(user: User) -> str:
    private_key = open(environ["JWT_ENCRYPTION_KEY_PATH"]).read().encode()
    expiration_time = now() + timedelta(days=3)

    payload_data = {
        "user_uuid": str(user.uuid),
        "email": user.email,
        "exp": expiration_time,
    }

    token = jwt.encode(payload_data, private_key, algorithm="RS256")
    return token
