"""
This file contains all the helpers for chats app
"""

import time
from os import environ

from django.contrib.auth import get_user_model

from helpers.caching import CustomRedisCaching

USER_QUEUE_CACHE_KEY = environ["USER_QUEUE_CACHE_KEY"]
USER_ID_HASH_CACHE_KEY = environ["USER_ID_HASH_CACHE_KEY"]
User = get_user_model()


def send_user_to_queue(user: User):
    redis_server = CustomRedisCaching()
    queue_users = redis_server.lrange(key=USER_QUEUE_CACHE_KEY)
    if user in queue_users:
        return False
    redis_server.rpush(USER_QUEUE_CACHE_KEY, [user])
    redis_server.hset(USER_ID_HASH_CACHE_KEY, str(user.uuid), int(time.time()))
    return True
