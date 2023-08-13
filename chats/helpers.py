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
    if user in queue_users:
        return False
    redis_server.rpush(settings.USER_QUEUE_CACHE_KEY, [user])
    redis_server.hset(
        settings.USER_ID_HASH_CACHE_KEY,
        str(user.uuid),
        int(time.time()),
    )
    return True


def get_user_pairs(users_list: list) -> list[tuple]:
    return [(users_list[index], users_list[index + 1]) for index in range(0, len(users_list), 2)]
