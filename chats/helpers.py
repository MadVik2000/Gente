"""
This file contains all the helpers for chats app
"""

import time
from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from chats.models import ChatSession, ChatSessionUser
from helpers.caching import CustomRedisCaching

User = get_user_model()


def send_user_to_queue(user: User):
    redis_server = CustomRedisCaching()
    queue_users = redis_server.lrange(key=settings.USER_QUEUE_CACHE_KEY)
    if user in queue_users:
        return False
    redis_server.rpush(settings.USER_QUEUE_CACHE_KEY, [user])
    redis_server.hset(
        settings.USER_ID_HASH_CACHE_KEY, str(user.uuid), int(time.time())
    )
    return True


def get_user_pairs(users_list: list) -> list[tuple]:
    return [
        (users_list[index], users_list[index + 1])
        for index in range(0, len(users_list), 2)
    ]


def create_session_and_session_users(
    users_list: list,
) -> tuple[bool, Union[str, tuple[ChatSession, ChatSessionUser]]]:
    users_pairs = get_user_pairs(users_list)

    chat_sessions = []
    chat_session_users = []
    try:
        for users in users_pairs:
            chat_session = ChatSession()
            chat_session.clean()
            chat_session.clean_fields()
            chat_sessions.append(chat_session)

            for user in users:
                chat_session_user = ChatSessionUser(
                    chat_session=chat_session, user=user
                )
                chat_session_user.clean()
                chat_session_users.append(chat_session_user)

        chat_sessions = ChatSession.objects.bulk_create(chat_sessions)
        chat_session_users = ChatSessionUser.objects.bulk_create(
            chat_session_users
        )

    except (ValidationError, IntegrityError) as error:
        return False, error

    return True, (chat_sessions, chat_session_users)
