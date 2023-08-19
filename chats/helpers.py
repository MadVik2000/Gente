"""
This file contains all the helpers for chats app
"""

import time

from django.conf import settings
from django.contrib.auth import get_user_model

from helpers.caching import CustomRedisCaching

User = get_user_model()


def send_user_to_queue(user: User, queue: str = settings.USER_DEFAULT_QUEUE_KEY):
    redis_server = CustomRedisCaching()
    queue_users = redis_server.hget(name=settings.USER_QUEUE_CACHE_KEY, key=queue.lower()) or []
    queue_users_email = [queue_user.get("email") for queue_user in queue_users]
    if user.email in queue_users_email:
        return False

    queue_users.append(
        {
            "user": user,
            "email": user.email,
            "queue_joining_time": time.time(),
        }
    )

    redis_server.hset(name=settings.USER_QUEUE_CACHE_KEY, key=queue.lower(), value=queue_users)
    return True


def get_user_pairs(users_list: list) -> list[tuple]:
    return [(users_list[index], users_list[index + 1]) for index in range(0, len(users_list), 2)]
