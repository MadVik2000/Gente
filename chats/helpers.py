"""
This file contains all the helpers for chats app
"""

import time

from django.conf import settings
from django.contrib.auth import get_user_model

from helpers.caching import CustomRedisCaching

User = get_user_model()


def send_user_to_queue(user: User):
    redis_server = CustomRedisCaching()
    queue_users = redis_server.lrange(key=settings.USER_QUEUE_CACHE_KEY)
    queue_users_email = [queue_user.get("email") for queue_user in queue_users]
    if user.email in queue_users_email:
        return False
    redis_server.rpush(
        key=settings.USER_QUEUE_CACHE_KEY,
        values=[
            {
                "user": user,
                "email": user.email,
                "queue_joining_time": time.time(),
            }
        ],
    )
    return True


def get_user_pairs(users_list: list) -> list[tuple]:
    return [(users_list[index], users_list[index + 1]) for index in range(0, len(users_list), 2)]
